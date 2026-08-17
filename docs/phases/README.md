# Phases

Create `NN-kebab-name.md` only after initialization. Read only the phase marked
`[>] IN PROGRESS` by default, plus the immediate predecessor's compact `Completion Record`
when present. A phase owns Goal, phase-specific Context, In scope, Out of scope, Tasks,
Acceptance criteria, relevant negative/security cases, and Verification.

Before a completed phase becomes `[x]`, persist its durable result under `## Completion Record`
according to `docs/system/HANDOFF_PROTOCOL.md`. Keep older phase bodies out of normal warm-up;
open them only when evidence or a historical dependency requires it.
