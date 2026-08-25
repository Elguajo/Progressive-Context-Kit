# Real-Agent Evaluations

Controlled model runs live conceptually here. Keep model, reasoning, repo snapshot,
permissions, tools, task wording, and acceptance criteria constant when comparing workflow
versions. Static contract coverage is not empirical quality evidence.

Use:
- `MODEL_EVAL_PROTOCOL.md` for the general quality/non-regression protocol;
- `EXECUTION_EFFICIENCY_PROTOCOL.md` for paired token/tool/runtime experiments;
- `RUN_RECORD.schema.json` as the canonical paired-eval per-run record format;
- `benchmark/` for the fixed six-scenario Execution Efficiency discovery pack;
- `cold-start/` for fresh-session Project Runtime transfer evaluation with one initial user message and no rescue prompting;
- `autoresearch/` for the evidence-driven one-hypothesis optimization lifecycle;
- `tools/prepare_agent_benchmark.py` to materialize clean baseline/candidate repositories;
- `tools/analyze_agent_eval.py` to validate controlled pairs and calculate paired deltas;
- `tools/prepare_cold_start_eval.py` to materialize fresh current-Runtime transfer scenarios;
- `tools/analyze_cold_start_eval.py` to evaluate complete cold-start suite runs against the external oracle;
- `tools/autoresearch.py` to create, evaluate, decide, validate, and list persistent Autoresearch experiments.

The broad benchmark discovers candidate waste patterns. A true Autoresearch experiment begins
only after a concrete observation exists, then tests one primary behavioral hypothesis with a
controlled candidate and records a `KEEP`, `MODIFY`, or `REMOVE` decision.

Cold-start transfer answers a separate question: whether the current Runtime can guide a fresh
agent correctly from the first user message. Preparing the pack or passing static tests is not
empirical transfer evidence; only recorded fresh-session model runs can produce that result.

These files, fixture builders, preparers, analyzers, cold-start oracles, Autoresearch records,
and lifecycle tooling are Framework Source-only research infrastructure and must not be packaged
into Project Runtime.
