# Layer Ownership

Each durable rule/fact gets one canonical owner.

- Global agent contract → universal engineering behavior, classification, grounding, safety, completion.
- Personal repo router → project context/workflow/tool routing.
- Brief → product outcome/users/scope/constraints/success.
- Architecture → current stack/system shape/trust boundaries/operational assumptions.
- Roadmap → phase order/status/current pointer.
- Current Phase → execution tasks/acceptance/verification.
- Completed Phase `Completion Record` → compact durable outcome/evidence/debt/cross-phase assumptions.
- `CONTEXT_MANIFEST.json` → optional non-obvious phase-specific context/Skill hints; never duplicate full docs.
- ADR → one consequential decision rationale.
- `TOOL_REGISTRY.json` → preferred branded capability mapping/install policy.
- `TOOLING_STATUS.json` → project-local persisted tooling availability/configuration cache.
- Skill/protocol → conditional detailed procedure.
- NEXT_SESSION → volatile continuation navigation, overwritten in place.
- LINEAGE → framework-maintenance evidence only, never normal task warm-up.

References/routing are allowed; copying the same long policy into multiple always-loaded layers is not.

## Agent adapters

Codex Personal uses `global/AGENTS.codex.md`; Claude Personal uses `global/CLAUDE.md`. Both share the same vendor-neutral repository router. Root `CLAUDE.md` imports `@AGENTS.md`; it must not import the Standalone profile directly because Personal Claude already receives universal behavior from `~/.claude/CLAUDE.md`.
