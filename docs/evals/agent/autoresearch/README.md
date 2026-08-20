# Autoresearch Optimization Loop

This directory is Framework Source-only research infrastructure for evidence-driven evolution of
Progressive Context. It must never enter Project Runtime.

Autoresearch begins after a discovery benchmark or real task trace reveals a concrete,
repeatable waste or quality pattern. A broad benchmark may discover candidates, but it is not
itself a one-variable Autoresearch experiment.

## Core loop

Use exactly this progression:

`OBSERVE -> HYPOTHESIZE -> CHANGE -> PAIRED EVAL -> DECIDE -> RECORD`

The default discipline is **one observation -> one hypothesis -> one primary candidate change**.
Do not stack several unmeasured behavioral changes into one experiment and then attribute the
combined result to one rule.

### 1. Observe

Start from real evidence: benchmark traces, paired outliers, repeated production-task traces, or
another auditable run source. Record the concrete pattern and evidence references. Do not start
from a preference for a rule.

### 2. Hypothesize

State a falsifiable explanation for the pattern and the expected measurable effect. Name the
primary metric or behavior that should change and what would count as no effect or regression.

### 3. Change

Create the smallest candidate change that can test the hypothesis. Keep unrelated framework
behavior fixed. If multiple files must change to express one behavior, that can still be one
primary change; multiple independent behavioral ideas cannot.

### 4. Paired eval

Use the controlled paired protocol in `../EXECUTION_EFFICIENCY_PROTOCOL.md` and run records from
`../RUN_RECORD.schema.json`. Keep model, reasoning, task, repository snapshot, tools,
permissions, environment, and token-accounting method controlled between arms.

Analyze records with:

`python3 tools/analyze_agent_eval.py runs.jsonl --format json > summary.json`

### 5. Decide

Every evaluated experiment ends with one explicit decision:

- **KEEP** — quality gate passes and the measured tradeoff is useful enough to retain;
- **MODIFY** — evidence is mixed/inconclusive or suggests a different formulation worth testing;
- **REMOVE** — the candidate has no useful effect, loses the tradeoff, or causes regression.

A `KEEP` decision is invalid when the paired analyzer quality gate is `FAIL`. Efficiency never
outvotes correctness, safety, security, or required completion behavior.

### 6. Record

Persist the experiment record under `experiments/EXP-NNNN.json` and index it in `REGISTRY.json`.
The record must preserve the observation, hypothesis, candidate change, immutable workflow
refs, evaluation evidence, result, and final decision rationale. Git history is the audit trail;
do not rewrite a decided record merely to make a later result look cleaner.

## Lifecycle

Experiment status is monotonic:

`PLANNED -> EVALUATED -> DECIDED`

A decided experiment is terminal. A `MODIFY` decision creates a **new** experiment with a new ID
that links back through `parent_experiment_id`; it does not reopen the old experiment.

## Tooling

Create a planned experiment:

```bash
python3 tools/autoresearch.py new \
  --observation "Candidate repeatedly rereads the same large file" \
  --hypothesis "A locate-then-slice instruction will reduce read volume" \
  --change "Make bounded inspection operational: locate, slice, widen only if unresolved" \
  --baseline-ref <immutable-ref> \
  --candidate-ref <immutable-ref> \
  --task-set execution-efficiency-v1/keyhole-read
```

Validate the registry and records:

```bash
python3 tools/autoresearch.py validate
```

Attach analyzer evidence and decide:

```bash
python3 tools/autoresearch.py decide EXP-0001 \
  --summary path/to/summary.json \
  --decision KEEP \
  --reason "Lower paired file reads/tokens with quality gate PASS"
```

`tools/autoresearch.py` validates lifecycle transitions and rejects `KEEP` when the analyzer
quality gate is not `PASS`.

## Claim discipline

An experiment supports only the change, task set, agents/models, sample size, and environment
actually evaluated. Record exploratory results as exploratory. Do not convert a small benchmark
win into a universal percentage claim. Prefer deleting or revising a rule that repeatedly fails
to produce measurable value over preserving it because it sounds reasonable.
