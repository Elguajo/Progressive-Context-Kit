# Migration Evidence

`ORIGINAL_CUSTOM_INSTRUCTIONS.txt` is an unchanged archival copy of the comprehensive
pre-progressive Custom Instructions. It is evidence, **not active instructions**.

- `ORIGINAL_CUSTOM_INSTRUCTIONS.sha256` pins the archival bytes.
- `COVERAGE_MATRIX.json` is the 12-section human index.
- `BEHAVIOR_CONTRACT.json` is the authoritative 147-rule atomic migration contract.
- `BEHAVIOR_IDS.sha256` pins the sorted rule-ID set against accidental deletion/rename.
- `MIGRATION_FROM_FULL_CUSTOM_INSTRUCTIONS.md` explains ownership and migration policy.
- `../evals/BEHAVIOR_SCENARIOS.json` exercises every atomic rule in representative scenarios.

`tools/behavior_contract.py` verifies active owners, semantic anchors, archived source-line
traceability, rule-ID pinning, scenario coverage, and Skill routes. `tools/audit.py` includes
that check as part of the framework quality gate.
