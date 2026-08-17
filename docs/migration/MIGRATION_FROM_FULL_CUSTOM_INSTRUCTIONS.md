# Migration from Full Codex Custom Instructions

The unchanged source `ORIGINAL_CUSTOM_INSTRUCTIONS.txt` contains the original comprehensive
12-section working agreement. Its SHA-256 is pinned so the baseline cannot silently drift.

## v1.2+ migration standard

Section-level coverage alone is too weak. v1.2+ therefore uses two layers:

1. `COVERAGE_MATRIX.json` — human-readable section → owner index.
2. `BEHAVIOR_CONTRACT.json` — authoritative **atomic rule** mapping.

The atomic contract currently contains **147 rules**. Every rule records:

- original section and source lines;
- semantic summary;
- one active canonical owner;
- an anchor that must remain present in that owner.

`BEHAVIOR_IDS.sha256` pins the sorted atomic rule-ID set so accidental rule deletion/rename
fails audit. `docs/evals/static/BEHAVIOR_SCENARIOS.json` contains representative scenarios, and every
atomic rule must be covered by at least one scenario. Every behavior-bearing line of the
archived source is also traceable to at least one atomic rule.

## Ownership summary

| Original section | Primary v1.2+ owners |
|---|---|
| `ROLE` | global Custom Instructions |
| `TASK_CLASSIFICATION` | global Custom Instructions + triggered decision/security workflows |
| `REPOSITORY_GROUNDING` | global Custom Instructions + personal context router |
| `ENGINEERING_PRINCIPLES` | global Custom Instructions |
| `DECISION_WORKFLOW` | `architecture-decision` Skill |
| `CODE_REVIEW_MODE` | `code-review` Skill |
| `IMPLEMENTATION` | global invariants + `implementation-execution` + `systematic-debugging` |
| `VALIDATION_LOOP` | `QUALITY_PROTOCOL.md` + implementation routing |
| `SAFETY_AND_APPROVALS` | global boundary + `security-sensitive-change` Skill |
| `DOCUMENTATION_UPDATE_APPROVAL` | `documentation-governance` Skill |
| `FINAL_REPORT` | global completion contract + `session-handoff` |
| `COMMUNICATION_STYLE` | global Custom Instructions |

Run:

```bash
python3 tools/behavior_contract.py
```

A removed owner, missing anchor, unknown Skill route, duplicate rule ID, uncovered original
section, or rule without scenario coverage makes the check fail.
