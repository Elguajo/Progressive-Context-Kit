# Cold-Start Runtime Transfer Eval

This suite tests a different claim from paired workflow benchmarks:

> Can a fresh coding-agent session use a newly installed Progressive Project Runtime correctly from the first user message, without hidden prior chat context or rescue prompting?

It is **Framework Source-only empirical-evaluation infrastructure**. None of this directory, the preparer, the analyzer, or its oracle data belongs in Project Runtime.

## Cold-start contract

For every scenario:

1. Prepare a fresh repository from the current Framework Source and the scenario fixture.
2. Start a new agent conversation with no reused conversation state.
3. Give the agent the exact contents of `prompt.md` as **one initial user message**.
4. Do not give the agent `oracle.json`, this README, scenario metadata, expected Skills, expected planning depth, or scoring criteria.
5. Do not add a clarification, reminder, or corrective hint to make the agent discover Progressive behavior. Any such extra instruction is a **rescue turn** and makes first-message transfer fail for that run.
6. Normal user interaction that the Runtime itself correctly requests is not a rescue. Example: choosing an architecture option after `architecture-decision` deliberately stops is part of the scenario, but the transfer observation is scored at the deliberate stop boundary.
7. Capture the actual trace/repository outcome, then create a run record using `RUN_RECORD.schema.json`.
8. Analyze one complete suite run with `tools/analyze_cold_start_eval.py`.

Static tests prove only that the pack is reproducible and its oracle is hidden from the agent repository. They do **not** prove model transfer quality.

## Scenario set

`SCENARIOS.json` defines eight routing/state cases:

1. greenfield `DIRECT`;
2. greenfield `FOCUSED`;
3. existing-project adoption;
4. unclear root-cause bug;
5. architecture fork with deliberate stop;
6. session continuation from hot project state;
7. change request after a completed Roadmap;
8. high-risk/public-contract work requiring `FULL` planning.

The task prompt intentionally does not name the expected Skill or planning depth. Expected behavior lives only in the external oracle.

## Prepare the suite

From a clean Framework Source checkout:

```bash
python3 tools/prepare_cold_start_eval.py
```

Optional:

```bash
python3 tools/prepare_cold_start_eval.py --agent codex
python3 tools/prepare_cold_start_eval.py --agent claude
python3 tools/prepare_cold_start_eval.py --scenario unclear-root-cause-bug
```

Default output:

```text
dist/agent-eval/cold-start-runtime-transfer-v1/
├── RUN_PLAN.json
└── scenarios/
    └── <scenario-id>/
        ├── prompt.md       # give this to the fresh agent
        ├── oracle.json     # evaluator only; never give to the agent
        └── repo/           # fresh Project Runtime + fixture/state
```

Each prepared repo is initialized as an independent clean Git repository. `RUN_PLAN.json` records the Framework Source commit, prompt hash, repo snapshot, and paths required to reproduce the run.

## Record a run

Create one JSON record per scenario. A complete run set uses the same `suite_run_id`, agent/model/reasoning profile, permissions, tools profile, and environment profile across all eight scenarios.

The observation records:

- whether the session was actually fresh;
- number of rescue turns;
- Skills observed in the agent trace/behavior;
- selected planning depth when applicable;
- whether the agent deliberately stopped for user direction when required;
- scenario-specific state/result checks;
- any material correctness, safety, or completion failure;
- optional token/tool/time metrics.

Do not infer a routed Skill solely because its file exists. Record it only when the trace, tool activity, or produced behavior provides evidence that the capability was actually activated.

## Analyze

```bash
python3 tools/analyze_cold_start_eval.py cold-start-runs.jsonl
```

A suite run passes transfer only when all required scenarios are present exactly once and every scenario satisfies all of these:

- `fresh_session = true`;
- `rescue_turns = 0`;
- required Skills were activated and forbidden Skills were not;
- planning depth matches the scenario oracle when applicable;
- deliberate-stop behavior matches the oracle;
- every required result/state check is true;
- no material hard failure is recorded.

This is a **transfer gate**, not a universal model-quality claim. Report exact agent/model/runtime ref, scenario count, failures, rescue turns, and remaining uncertainty. One successful suite run is evidence that this configuration transferred on these scenarios; it is not proof that every model or repository will behave identically.
