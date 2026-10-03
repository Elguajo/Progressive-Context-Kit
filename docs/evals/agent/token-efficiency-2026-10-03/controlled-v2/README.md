# Controlled harness v2 — historical Codex diagnostic rerun

Status: harness repair and Codex diagnostic rerun completed in the main working tree.
Claude remains deferred by user; the broader optimization plan remains IN PROGRESS.
This dataset is separate from the first historical pilot; no current-workflow saving or
accepted RTK/Serena optimization is claimed.

## Implemented harness repair

Opt-in experiment setting `harness_profile=controlled-v2` enables two measured setup repairs:

- Add only the empty tests package marker where a test directory exists. The exact declared
  root unittest discovery now finds real tests on Python 3.12. Application code, test assertions,
  task wording and acceptance are unchanged.
- Keep task repos in external opaque workspaces. Generated project-state seeds and initial Git
  metadata are neutral; control-only experiment/arm maps, prompts and results stay in the pack.
  Both explicit and default temporary destinations are checked before output replacement.
  Existing workspace directories are never overwritten.

The default historical experiment, fixture content, Git metadata and pack layout remain
unchanged. No agent runner/orchestrator, hooks, proxy or global configuration were added.
Historical artifacts are retained. `--workspace-root` is optional for this new mode; the default
retained temporary directory and relative repo paths are recorded in [RUN_PLAN.json](RUN_PLAN.json).

## Preparation and controls

Prepared six pairs / twelve clean task repos. [PREPARATION_CHECKS.json](PREPARATION_CHECKS.json)
checks external neutral paths, generated seeds, Git history, clean working trees, and nonempty
root discovery in every unittest fixture. Polling uses its declared slow command and has no
unittest fixture. Harness/TASKS source hashes are retained in [HARNESS_SHA256.json](HARNESS_SHA256.json).
[EXPERIMENT.json](EXPERIMENT.json) pins the same historical workflow SHAs as the first pilot.
This is a repaired diagnostic comparison, not a new single-optimization experiment.

Codex CLI 0.147.0, gpt-5.6-sol, high reasoning; fresh ephemeral sessions,
ignore-user-config, workspace-write sandbox; exact original prompt plus acceptance in each arm.
Runtime target remains both, but only Codex is executed. Native tools and existing host Skill
catalogs remain available equally; optional framework tools are not routed. Provider usage,
cache and complete native JSONL traces are collected without invented measurements. The same
input+output accounting includes cache/reasoning subsets once. Judge/preflight usage is separate.

Prepare explicitly with:

```bash
python3 tools/prepare_agent_benchmark.py \
  --experiment docs/evals/agent/token-efficiency-2026-10-03/controlled-v2/EXPERIMENT.json \
  --repetitions 1 --output dist/agent-benchmark/controlled-v2-2026-10-03
```

Use a fresh disposable output path when repeating: this command replaces the control pack.
The kit only prepares/analyzes. The implementing engineer invokes existing clients outside
kit tooling. Candidate prompt delivery references no control paths. Raw invocations and timing
are kept in the control pack's evidence directory, outside the candidate task roots.

## Result

Six pairs / 12 fresh completed task invocations and six blinded A/B reviews. All twelve
implementations passed independent required-code validation; exact root discovery ran real
tests. Both arms have six accepted tasks, no hard failures, and no incomplete task attempt in
this dataset. Judges invoked no tools and never saw the private arm map. The strict analyzer
accepted all run/judge/evidence records and returned:

- Median paired total-token delta: **-1.36%**, below the required 10% useful-effect threshold.
- Quality gate: **FAIL**, median paired quality delta **-0.05 / 3.00** with zero tolerance.
- Recorded tokens per successful task: **263,468.83 baseline**, **217,228.33 candidate**.
  All task attempts are included; no missing provider consumption exists within this dataset.

| Scenario | Baseline reported tokens | Candidate reported tokens | Paired delta |
|---|---:|---:|---:|
| recon-batch | 503,527 | 186,963 | -62.87% |
| keyhole-read | 110,177 | 133,047 | +20.76% |
| environment-probe | 240,574 | 319,129 | +32.65% |
| validation-convergence | 231,699 | 178,681 | -22.88% |
| failure-pivot | 249,368 | 299,640 | +20.16% |
| polling-discipline | 245,468 | 185,910 | -24.26% |

The large reconnaissance reduction is not an acceptable standalone win: its faster artifact
leaves the active Phase, Roadmap and NEXT_SESSION in progress despite reporting completion.
The blinded judge prefers the artifact that reconciles required project state. The aggregate
sum/per-success figure is dominated by this outlier; inspect per-pair and per-dimension
findings instead of selecting the most favorable summary. Several other scenarios use more
candidate tokens. No routing/instruction optimization is accepted, registered as KEEP, or
attributed to current PCK. Neither this one-pair sample nor its difference from the first pilot
establishes a stable causal saving.

See [run records](codex-runs.jsonl), [judge records](judge-records.jsonl),
[summary](codex-summary.json), and [observable trace counters](MEASUREMENTS.json).
The control-only arm map and full anonymous artifacts are preserved in this directory.
`turns` counts outer client turns, `tool_calls` observable completed command/file-change items,
and `file_reads` the shell inspection-request proxy defined in the first pilot, with item IDs.
Hidden model requests/waits, initial/peak context, cost, and full physical file-open counts are
not reported by the native client; no estimates replace them. Input includes cached input;
output includes reasoning. Both subsets are counted only once. Preflight/judge usage is separate
from task consumption. No compaction occurred, and polling-call counts are unavailable.

## Verification and continuation

Focused harness tests: 17 passed, including exact default fixture hashes matched against the
preserved first pilot. Canonical gate: 243 tests / 11 checks — PASS; local Standalone release build — PASS.
Source audit: 0 errors/warnings; Runtime audit: 0 errors and 12 existing Skill collision warnings. Source/Runtime research exclusion and unchanged instruction
budgets/project-owned seeds are checked by the existing gate and builder. This harness fix
adds no executor, scheduler, hooks, proxy, global settings or hot workflow instructions.

At collection time the working tree was RUNNABLE / GREEN on main, with local uncommitted changes.
The nearest remaining
optimization boundary is a new single-hypothesis candidate supported by a repeatable trace
observation, fixed current workflow SHAs, adequate paired sample and non-inferior quality.
Do not promote incomplete project-state updates as an efficiency optimization. Existing
RTK/Serena routing remains unchanged; eligible compact-output gains must be measured rather
than inferred from synthetic character compression. Claude and two-agent confirmation remain
deferred; no two-agent KEEP is possible from these records.
