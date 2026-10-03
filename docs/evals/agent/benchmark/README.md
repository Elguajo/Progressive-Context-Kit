# Execution Efficiency Benchmark Pack

This directory defines the fixed real-agent experiment for Progressive Context Execution
Efficiency. It is **Framework Source-only research infrastructure** and is never part of
Project Runtime.

## What is fixed

`EXPERIMENT.json` pins two immutable workflow refs:

- baseline: `b5d68e6ae258f02f7c5829e8f8bac54dd4d39a4a` — last main commit before the first
  Execution Efficiency rule;
- candidate: `8a8e21f16cb30d5cffe7c493a6c31dc17bfaa503` — completed Phase 6 workflow.

`TASKS.json` contains six tasks, one primary scenario for each mechanism:

1. batch repository reconnaissance;
2. bounded/keyhole reads;
3. single-pass environment probing;
4. convergent validation;
5. repeated-failure hypothesis pivot;
6. bounded polling for a long-running validation command.

Neither the task prompt nor its acceptance criteria name the mechanism under test. Mechanism
metadata lives outside the prepared repo so the agent is not coached toward the desired
behavior.

## Prepare the pack

From a full clone of this repository:

```bash
python3 tools/prepare_agent_benchmark.py --repetitions 1
```

The default one repetition is an exploratory harness smoke test, not enough for a stable
percentage claim. Before publishing a median-efficiency claim, use at least five paired
repetitions per task:

```bash
python3 tools/prepare_agent_benchmark.py --repetitions 5
```

The builder requires Git history containing both pinned refs. If the clone is shallow, fetch
history first. It exports each pinned workflow with `git archive`, builds its Standalone
Project Runtime, injects that Runtime into a copy of the same raw fixture, replaces
uninitialized Runtime seeds with identical minimal ACTIVE project state, initializes a clean
Git repository, and writes `RUN_PLAN.json`.

Prepared output defaults to:

`dist/agent-benchmark/execution-efficiency-v1/`

For a new single-change experiment, copy the configuration to a new research file and set
`experiment_id`, distinct immutable 40-character baseline/candidate Git SHAs, and the agent
target. Keep the six task prompts and acceptance criteria fixed. Then run:

```bash
python3 tools/prepare_agent_benchmark.py --experiment path/to/experiment.json --repetitions 1
```

Without `--experiment`, the historical pinned comparison remains unchanged. A custom
experiment defaults to `dist/agent-benchmark/<experiment_id>/`; `--output` overrides that
location. The selected configuration and its SHA-256 are preserved in `RUN_PLAN.json`.
Only Standalone preparation is currently supported; unsupported profiles, moving refs,
identical workflow refs, and invalid repetition counts are rejected before output replacement.
Use a fresh disposable output location: preparing a pack replaces an existing output directory.
Historical runs diagnose the historical change, not the current PCK version.

For new diagnostic datasets, set `"harness_profile": "controlled-v2"` in the experiment
configuration. This opt-in mode adds an empty `tests/__init__.py` where a test directory
exists, so the declared root-level unittest discovery finds real tests. Task prompts,
acceptance criteria, application code, and test assertions are unchanged. Missing or explicit
`"historical"` preserves the old fixtures and layout.

Controlled mode puts task repos in retained external workspaces with opaque names, uses
neutral project seeds and Git metadata, and keeps experiment/arm labels in the control pack
only. `RUN_PLAN.json` records `harness_profile`, `workspace_root`, and each repo path relative
to the control pack (it may begin with `..`). Resolve paths against the pack directory;
do not infer arm identity from directory names. Optional `--workspace-root PATH` must name a
new, neutral directory outside Framework Source and outside the control pack; existing
workspace directories are never replaced. Without it, a new `local-tasks-*` temporary
directory is created and retained. Preserve needed task artifacts before manually cleaning
these workspaces. Control-pack output replacement behavior is unchanged.

Use a new experiment ID/dataset for controlled mode. Its fixture/setup hashes differ from
historical mode, so do not pool the two datasets or attribute their difference to a workflow
optimization. The default historical configuration and pinned refs remain unchanged.

Each pair has this shape:

```text
tasks/<task-id>/
├── prompt.md
├── acceptance.md
└── r01/
    ├── baseline/repo/
    └── candidate/repo/
```

`prompt.md` and `acceptance.md` stay outside the agent repository. Give the agent the exact
contents of **both files in one initial user message**, with prompt first and acceptance
criteria second. Do not copy benchmark mechanism metadata or the `interpretation` field into
the agent message.

## Run a pair

For each pair, keep constant:

- agent product and exact model version;
- reasoning/effort setting;
- tool access and permissions;
- machine/container/environment;
- task wording and acceptance criteria.

Only the prepared workflow arm may differ.

Run the baseline repo and candidate repo as fresh sessions. Do not reuse conversation state
between arms. Use the same combined prompt + acceptance message. Capture the provider/agent
trace and usage data.

Do not compare Codex baseline to Claude candidate. Codex and Claude are separate experiments;
each needs its own paired records.

Store each agent/model/reasoning/accounting/workflow comparison in its own run file. The
analyzer rejects pooling different comparisons. Do not estimate usage from trace bytes or
the static context report. Preserve provider usage as reported, document whether input
already includes cached input and whether output includes reasoning, and do not double count.
Unavailable optional measurements remain null or absent. Never create successful outcomes
from an agent's final message alone.

## Produce run records

Create one record per run following `../RUN_RECORD.schema.json`. Use the task fixture digest
from `RUN_PLAN.json` as `controls.repo_snapshot`; the arm-specific local Git commit is only a
local integrity marker because workflow-owned files intentionally differ between arms.

`RUN_PLAN.json` already contains the SHA-256 values for the exact `prompt.md` and
`acceptance.md`; use them as `controls.task_sha256` and `controls.acceptance_sha256`. Record
identical control-profile strings in both records for tools, permissions, and environment.

Required measured metrics are:

- total tokens;
- turns;
- tool calls;
- file reads;
- wall time.

Also record input/output/cache/cost/context metrics when the agent exposes them. Quality is
scored 0–3 with higher always better. A material correctness/safety/completion regression is
`hard_pass=false` even if the candidate is cheaper.

Then analyze the combined JSONL:

```bash
python3 tools/analyze_agent_eval.py runs.jsonl --require-pass
```

The additive `baseline_outcomes` and `candidate_outcomes` summaries include successful and
failed run counts, total tokens across all attempts, and `tokens_per_successful_task`.
This last value divides all attempt tokens by successful tasks, returning null if none
succeeded. With blinded judging, success uses the judge's hard-failure assessment, just like
the quality gate. Existing run-record schema and median fields are retained.

## Scenario interpretation

The six tasks are diagnostic, not independent proof that a particular rule caused every
observed saving. Use traces to confirm the intended mechanism actually differed between arms.
For example, fewer tokens in the keyhole task are only evidence for bounded reads if the trace
shows materially narrower inspection; otherwise record the result but do not attribute it to
that mechanism.

The polling task intentionally waits about 35 seconds. Its polling-specific interpretation is
valid only when the runner/harness can return control while the command remains in progress.
If execution blocks until completion, the task still checks correctness/validation but cannot
measure polling behavior.

## Claim discipline

One repetition is exploratory. Five repetitions per task is the minimum configured threshold
for a stable median claim, not a statistical equivalence guarantee. Report agent/model,
workflow refs, repetitions, task set, token-accounting method, paired medians, quality gate,
hard regressions, and uncertainty. Never infer a universal `-X%` from this benchmark alone.
