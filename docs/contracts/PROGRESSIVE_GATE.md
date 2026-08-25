# Progressive Framework Gate

Use `python3 tools/gate.py` as the canonical Framework Source verification entrypoint.

**One command owns the Framework Source verification sequence.** Individual validators remain independently executable and keep ownership of their own logic; the gate only orchestrates them.

The default gate runs, in order:

1. profile mirror integrity;
2. Skill mirror integrity;
3. inherited Behavior Contract;
4. Progressive Framework Contract and protected invariants;
5. Tool Adapter Protocol integrity;
6. Routing Integrity;
7. Autoresearch record integrity;
8. duplication audit;
9. Framework Source audit;
10. context-budget report;
11. framework unit/regression tests.

The gate is fail-fast. A child failure is reported with the failed check id and the gate exits non-zero.

`--skip-unit-tests` exists only for nested release-builder tests or bounded local iteration. It must not be treated as the normal pre-submit gate.

## Scope boundary

This gate is **Framework Source-only** and is not packaged into Project Runtime. Installed Runtime verification remains `.progressive/tools/audit.py`, `.progressive/tools/context_compile.py`, plus task-relevant project validation.

A `PROGRESSIVE GATE: PASS` means every configured Framework Source static/integrity check actually ran and passed. It is **not** evidence that a model follows the framework, passes the cold-start transfer suite, or achieves universal quality/token claims. Empirical model evaluations remain separate under `docs/evals/agent/`.
