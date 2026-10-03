# Token Efficiency Plan

Approved scope: implement the user's token-efficiency plan for Codex and Claude.
This is Framework Source-only research, not Project Runtime or normal startup context.
The English text below preserves the agreed plan's scope and acceptance criteria.

## Goal and boundaries

Measure complete task consumption reproducibly on Codex and Claude, then retain only
optimizations that preserve correctness, safety, and task completion. Start with PCK and
its existing RTK/Serena adapters. Defer Headroom, LLMLingua, TOON, global hooks, and proxies
until measurements justify them. Use fresh external client sessions; do not add an agent
executor or orchestrator to PCK. The implementing engineer prepares and collects the runs.

## 1. Reproducible measurement

- Separate persistent instructions, skill metadata, and on-demand context in the static report.
  Label `chars / 4` as an estimate, never a provider token or billing measurement.
- Refresh the size comparison with the version and measurement scope. Instruction shrinkage
  does not establish complete-task savings.
- Add optional `--experiment PATH` to `tools/prepare_agent_benchmark.py`, preserving its
  default behavior and historical pinned comparison.
- Pin baseline and candidate to distinct immutable Git SHAs for each single-change experiment.
- Retain the existing run-record format. Collect provider input/output/total tokens, cache,
  calls, reads, time, and cost when available; do not invent missing measurements.
- Report successful/failed runs and total tokens across all attempts divided by successful
  tasks. Return `null` when there are no successful tasks.
- Analyze Codex and Claude separately. Keep research artifacts out of Project Runtime.

## 2. Diagnostic pilot

Use the existing six scenarios: reconnaissance, bounded reads, environment probing,
validation convergence, repeated-failure pivot, and long-command polling.

- Start with one pair per scenario per agent: 24 task runs per comparison, excluding judging.
- Use the historical pinned comparison for the first diagnostic pilot; do not attribute its
  results to the current kit.
- Keep model, reasoning, task, environment, permissions, and available tools identical
  between arms. Use fresh sessions and the exact prompt plus acceptance criteria.
- Verify artifacts and commands; use the existing blinded A/B judging procedure for behavior.
- Identify repeatable waste in traces: rereads, context reloads, noisy output, duplicate
  discovery, redundant validation, and failed attempts.
- Register a one-hypothesis experiment only after an actual observation exists.
- Check existing Claude clients. Installation or configuration of missing Claude/RTK tooling
  requires the repository's separate approval. Do not claim two-agent results without Claude.

## 3. Optimization order

1. RTK: test supported compact output, exit-code preservation, critical diagnostics, original
   retrieval, and raw-output fallback. Make it available in both arms; vary routing only.
2. Serena: test known-symbol definitions/references instead of full-file reads. Preserve native
   fallback and the boundary with Semble intent-based discovery.
3. Context/rereads: change the compiler, pointers, or an existing Skill only if traces establish
   a concrete issue. Preserve acceptance criteria, the active checkpoint, and dependencies.
4. Instructions/validation: remove proven duplication or move conditional procedures to
   on-demand owners. Do not weaken mandatory validation.

Do not introduce universal rules, additional tools, or repository maps without evidence.
Use `OBSERVE -> HYPOTHESIZE -> CHANGE -> PAIRED EVAL -> DECIDE -> RECORD` for each candidate.

## 4. Confirmation and acceptance

- Confirm promising candidates with at least five pairs per affected scenario per agent,
  then smoke-test all six scenarios for side effects.
- Full six-scenario confirmation on both agents is 120 task runs per comparison. Reuse pilot
  records only when all controls match.
- Require at least a 10% reduction in median paired tokens on affected scenarios. This is a
  candidate acceptance threshold, not a promised saving.
- KEEP only when both agents meet the threshold, both quality gates PASS, no material
  regressions exist, and tokens per successful task do not increase.
- MODIFY mixed, insufficient, or one-agent-only results through a new linked experiment.
- REMOVE ineffective candidates or those regressing correctness, safety, or completion.

## 5. Verification and release

- Test experiment selection, old-record compatibility, failed-attempt accounting, and no-success
  input. For context changes test deduplication, required information, and compaction continuity.
- For adapter changes test unavailable/failing tools and recovery of complete diagnostics.
- Run focused tests and `python3 tools/gate.py`; generate and verify Runtime using the existing
  release builder. Preserve public compatibility, instruction budgets, and project-owned state.
- Publish only measured agent/model/sample/accounting/quality results and their limitations.
  Keep experimental evidence out of startup context.

Expected outcome: a current report, reproducible two-agent comparisons, and only empirically
supported optimizations.

## Implementation checkpoint

Status: IN PROGRESS; measurement infrastructure is RUNNABLE / GREEN. Static report and
baseline comparison updated, optional experiment configuration/provenance implemented,
and all-attempt accounting added without changing the existing run schema. Focused tests:
38 passed; canonical gate: 238 tests, 11/11 checks; local Standalone release build: PASS.

Historical Codex diagnostic pilot: six pairs / 12 completed invocations with six blinded A/B
reviews. Median paired token delta +1.77%; quality gate FAIL. Each arm completed five accepted
tasks; both environment tasks failed mandatory discovery in the historical fixture. One
additional account-limit interruption has unknown usage and is preserved separately.
No current-version saving or accepted optimization is claimed.

User approved official local Claude Code and RTK installation: verified versions 2.1.285 and
0.51.0. Hooks/proxy integration and telemetry remain disabled. Claude is unauthenticated;
the user explicitly deferred Claude runs. Two-agent KEEP and confirmation remain pending.
Source-only [implementation evidence and continuation checkpoint](token-efficiency-2026-10-03/README.md)
preserve controls, metrics, verification, limitations and the nearest unresolved target.

### Controlled harness follow-up

User approved continuation directly on main. Opt-in `controlled-v2` fixes test discovery and
removes experiment/arm labels from task paths, initial seeds and Git metadata, while preserving
historical defaults and evidence. Preparation verified twelve clean neutral task repos; all
six historical default fixture hashes match the preserved first pilot. Focused harness tests:
17 passed; final canonical gate/release evidence is linked in the controlled report.

Separate Codex rerun completed: six pairs / twelve validated implementations and six blinded
reviews. Median paired tokens -1.36%, quality gate FAIL (-0.05 / 3.00). No new optimization is
accepted; Claude and two-agent confirmation remain deferred. Larger wins caused by omitted
project-state updates are not acceptable. See the [result and continuation boundary](token-efficiency-2026-10-03/controlled-v2/README.md).
