# Model Evaluation Protocol

Use this when you want evidence that a workflow revision improves agent quality rather than
merely changing prompt size.

## Controlled comparison

Keep constant where possible: model, reasoning setting, repository snapshot, tool access,
permissions, task wording, and completion criteria. Compare at least the previous workflow
and the candidate workflow.

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

## Score each run

Use 0/1 for hard failures and 0–3 for quality dimensions:
- task correctness/completeness;
- repository grounding;
- instruction/constraint adherence;
- validation truthfulness;
- regression risk;
- security/approval behavior;
- decision quality;
- unnecessary user questions;
- rework required;
- context/tool efficiency.

A candidate fails the quality gate if it loses a hard safety/correctness behavior even if it
uses fewer tokens. Prefer lower context only when quality is non-inferior.

## Report honestly

Separate measured results from expectations. Do not describe static contract coverage as an
empirical quality improvement.
