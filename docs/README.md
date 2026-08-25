# Documentation Map

Normal coding sessions must **not** recursively read this directory.

## Default project state
- `project/PROJECT_BRIEF.md`
- `project/ARCHITECTURE.md`
- `project/ROADMAP.md`
- the one current phase under `phases/`
- optional `project/CONTEXT_MANIFEST.json` hints
- only relevant ADR/code/tests/schemas/current docs

`tools/context_compile.py` can assemble this deterministically.

## On-demand framework reference
- `system/` — context, quality, ownership, handoff, tool routing, change control; `LINEAGE.md` is framework-maintenance-only.
- `contracts/` — Progressive Framework Contract.
- `migration/` — unchanged original Custom Instructions + inherited atomic Behavior Contract.
- `evals/static/` — machine-checkable scenarios; no model execution.
- `evals/agent/` — controlled real-agent evaluation protocol.
- `integrations/` — branded preferred tool registry/adapters; read only for selection/setup/routing.

## Human-only documentation
`human/GETTING_STARTED.md` is for people installing/using the framework, and `human/TECHNICAL_REFERENCE.md` is for integration and maintenance details. They are not normal agent warm-up context and are intentionally excluded from the Project Runtime build.

`DESIGN_RATIONALE.md`, `TOKEN_BUDGETS.md`, `BASELINE_COMPARISON.md`, and `COMPATIBILITY.md` are also framework/reference docs, not normal task warm-up context.
