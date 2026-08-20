# Model Evaluation Protocol

Use this when you want evidence that a workflow revision improves agent quality rather than
merely changing prompt size.

## Controlled comparison

Keep constant where possible: model, reasoning setting, repository snapshot, tool access,
permissions, task wording, and completion criteria. Compare at least the previous workflow
and the candidate workflow. Record immutable workflow refs so the comparison can be repeated.

For token/tool/runtime efficiency experiments, use
`docs/evals/agent/EXECUTION_EFFICIENCY_PROTOCOL.md`, record each run with
`RUN_RECORD.schema.json`, and compare paired records with `tools/analyze_agent_eval.py`.

## Scenario set

Select from `BEHAVIOR_SCENARIOS.json`, including at minimum:
- trivial edit;
- directed implementation;
- architecture decision + stop;
- rejected core strategy and rejected local detail;
- repository grounding with unrelated edits;
- unclear root-cause bug;
- code review;
- validation failure/unavailable environment;
- security anti-pattern refusal;
- high-risk approval boundary;
- durable documentation approval;
- clean completion/handoff.

Execution-efficiency claims must additionally exercise reconnaissance batching, bounded
inspection, environment probing, convergent validation, repeated-failure pivoting, and
long-running command polling.

## Score each run

Use 0/1 for hard failures and 0–3 for quality dimensions. All 0–3 scores are oriented so
**higher is better**:
- task correctness/completeness;
- repository grounding;
- instruction/constraint adherence;
- validation truthfulness;
- regression safety;
- security/approval behavior;
- decision quality;
- question efficiency;
- rework avoidance;
- context/tool efficiency.

A candidate fails the quality gate if it loses a hard safety/correctness behavior even if it
uses fewer tokens. Prefer lower context/execution cost only when quality is non-inferior.

## Report honestly

Separate measured results from expectations. Do not describe static contract coverage as an
empirical quality improvement. Report sample size, exact model/workflow refs, task set,
accounting method, paired efficiency deltas, quality deltas, hard regressions, and remaining
uncertainty. Small samples are exploratory; absence of a detected quality loss is not proof of
behavioral equivalence.
