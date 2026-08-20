# Execution Efficiency Evaluation Protocol

Use this protocol to measure whether execution-efficiency changes reduce total task cost
without weakening engineering quality. This is Framework Source research evidence only; it is
not part of Project Runtime.

## Hypothesis

Candidate workflow should reduce dynamic execution cost while remaining non-inferior on
correctness, safety, task completion, and engineering quality.

Do not infer savings from prompt size or static contract coverage. Measure real agent runs.

## Controlled paired design

For every pair keep constant:
- agent product and model version;
- reasoning/effort setting;
- repository snapshot;
- task wording and acceptance criteria;
- tool availability and permissions;
- environment image/runtime where practical.

Only the workflow under test should differ. Record the exact baseline and candidate
`workflow_ref` (commit, tag, or immutable artifact identifier).

Use the same `pair_id` for baseline and candidate runs. Repeat pairs when practical because
agent runs are nondeterministic; five or more repetitions per task is preferred for claims
about stable median effects, but smaller samples remain useful as exploratory evidence.

## Minimum task coverage

Include tasks that can exercise the execution-efficiency guarantees:
1. repository reconnaissance across several independent facts;
2. targeted inspection inside a large file/output;
3. implementation with several knowable environment prerequisites;
4. normal implementation whose required validation goes green;
5. unclear bug where the same check can fail repeatedly;
6. long-running build/test command where polling is possible.

The canonical fixed pack for these six mechanisms is `benchmark/EXPERIMENT.json` plus
`benchmark/TASKS.json`; materialize it with `tools/prepare_agent_benchmark.py` rather than
silently changing task wording between experiments.

Also keep the broader quality scenarios from `MODEL_EVAL_PROTOCOL.md` when making a release
quality claim.

## Record format

Write one JSON object per run using `RUN_RECORD.schema.json`. JSONL is recommended.

Required comparison metrics:
- `total_tokens`;
- `turns`;
- `tool_calls`;
- `file_reads`;
- `wall_time_seconds`.

Record when available:
- `input_tokens`;
- `output_tokens`;
- `cache_read_tokens`;
- `cost_usd`;
- `initial_context_tokens`;
- `peak_context_tokens`.

`total_tokens` must use the same accounting rule in both arms of an experiment. If the
provider does not report it, use `input_tokens + output_tokens` consistently and state that in
`token_accounting`.

## Quality scoring

All quality dimensions are 0–3 and **higher is better**:
- task correctness/completeness;
- repository grounding;
- instruction/constraint adherence;
- validation truthfulness;
- regression safety;
- security/approval behavior;
- decision quality;
- question efficiency (no unnecessary user questions);
- rework avoidance;
- context/tool efficiency.

`hard_pass=false` is reserved for material correctness, safety, security, destructive-action,
or completion-contract failures. Explain each in `hard_failures`.

## Comparison

Run:

`python3 tools/analyze_agent_eval.py path/to/runs.jsonl`

The analyzer:
- validates that each `pair_id` has exactly one baseline and one candidate;
- rejects pairs whose controlled fields differ;
- reports arm medians;
- reports median **paired** percentage deltas for efficiency metrics;
- reports paired quality deltas;
- fails the quality gate on any baseline-pass → candidate-fail hard regression;
- otherwise applies the configured quality non-inferiority tolerance.

A lower efficiency metric is better. A positive quality delta is better.

## Autoresearch loop

1. collect traces from representative tasks;
2. identify one concrete waste pattern;
3. change one rule/routing behavior when possible;
4. run paired baseline/candidate evaluations;
5. inspect hard regressions and outlier pairs, not only aggregate medians;
6. keep the change only when the quality gate passes and the measured tradeoff is useful;
7. record the accepted/rejected hypothesis and its evidence before testing the next change.

Do not stack multiple unmeasured optimizations and attribute the combined result to one rule.

## Claim discipline

Static tests prove rule presence and routing, not empirical quality or token savings.
Small samples are exploratory. Report sample size, model/version, task set, workflow refs,
token-accounting method, medians, paired deltas, hard regressions, and remaining uncertainty.
Do not claim equivalence or a universal percentage saving unless the experiment design
actually supports that claim.
