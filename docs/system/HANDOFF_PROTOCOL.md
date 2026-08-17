# Handoff Protocol

Classify the session `IN PROGRESS`, `PHASE COMPLETE`, or `PROJECT COMPLETE`.
Roadmap stays canonical for phase status.

## Phase completion transaction

When a phase satisfies its acceptance criteria:

1. persist the durable phase result in its `## Completion Record` **before moving the Roadmap marker**;
2. update Architecture/ADR/other canonical owners first when system shape or a consequential decision changed; the Completion Record should reference effects, not duplicate full rationale;
3. mark the completed phase `[x]` and exactly one next phase `[>]` when one exists;
4. overwrite `NEXT_SESSION.md` in place with only the hot state needed to continue.

A Completion Record is compact durable history. Capture only:
- **Delivered** — capabilities/artifacts that now exist;
- **Validation Evidence** — checks actually observed and their results;
- **Decisions Affecting Later Phases** — concise consequences and ADR/reference when applicable;
- **Deviations / Technical Debt** — known gaps that survived completion;
- **Handoff to Next Phase** — assumptions/capabilities the next phase may safely rely on.

Do not turn a Completion Record into a session diary, diff summary, or duplicate specification. If the
session remains `IN PROGRESS`, keep the phase active and do not fabricate a completion record.

On project completion every phase is `[x]` and none is `[>]`.

## NEXT_SESSION semantics

`NEXT_SESSION.md` is volatile hot navigation, not project history. Overwrite it on each meaningful
handoff; do not create an accumulating chain of `NEXT_SESSION_001.md`, `NEXT_SESSION_002.md`, etc.
It contains only current phase, completed work from the just-ended session, verification,
blockers/uncertainty, next action, and a ready-to-copy prompt. Durable completed-phase history belongs
in that phase's Completion Record; full technical history belongs in version control when available.
