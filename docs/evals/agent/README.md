# Real-Agent Evaluations

Controlled model runs live conceptually here. Keep model, reasoning, repo snapshot,
permissions, tools, task wording, and acceptance criteria constant when comparing workflow
versions. Static contract coverage is not empirical quality evidence.

Use:
- `MODEL_EVAL_PROTOCOL.md` for the general quality/non-regression protocol;
- `EXECUTION_EFFICIENCY_PROTOCOL.md` for paired token/tool/runtime experiments;
- `RUN_RECORD.schema.json` as the canonical per-run record format;
- `benchmark/` for the fixed six-scenario Execution Efficiency experiment pack;
- `tools/prepare_agent_benchmark.py` to materialize clean baseline/candidate repositories;
- `tools/analyze_agent_eval.py` to validate controlled pairs and calculate paired deltas.

These files, fixture builders, preparer, and analyzer are Framework Source-only research
infrastructure and must not be packaged into Project Runtime.
