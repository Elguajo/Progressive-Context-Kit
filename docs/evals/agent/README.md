# Real-Agent Evaluations

Controlled model runs live conceptually here. Keep model, reasoning, repo snapshot,
permissions, tools, task wording, and acceptance criteria constant when comparing workflow
versions. Static contract coverage is not empirical quality evidence.

Use:
- `MODEL_EVAL_PROTOCOL.md` for the general quality/non-regression protocol;
- `EXECUTION_EFFICIENCY_PROTOCOL.md` for paired token/tool/runtime experiments;
- `RUN_RECORD.schema.json` as the canonical per-run record format;
- `benchmark/` for the fixed six-scenario Execution Efficiency discovery pack;
- `autoresearch/` for the evidence-driven one-hypothesis optimization lifecycle;
- `tools/prepare_agent_benchmark.py` to materialize clean baseline/candidate repositories;
- `tools/analyze_agent_eval.py` to validate controlled pairs and calculate paired deltas;
- `tools/autoresearch.py` to create, evaluate, decide, validate, and list persistent Autoresearch experiments.

The broad benchmark discovers candidate waste patterns. A true Autoresearch experiment begins
only after a concrete observation exists, then tests one primary behavioral hypothesis with a
controlled candidate and records a `KEEP`, `MODIFY`, or `REMOVE` decision.

These files, fixture builders, preparer, analyzer, Autoresearch records, and lifecycle tooling
are Framework Source-only research infrastructure and must not be packaged into Project Runtime.
