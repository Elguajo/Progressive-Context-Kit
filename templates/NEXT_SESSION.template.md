# Next Session

> Volatile hot context. Overwrite this file on each meaningful handoff only when navigation/state changes. Task prompts and their evidence stay in the owning Phase; do not copy an executable task prompt here. Durable completed-phase history belongs in `docs/completions/` with only a compact bridge in the completed phase `Completion Record`.

Outcome: <IN PROGRESS | PHASE COMPLETE | PROJECT COMPLETE>

## Current phase
<exact Roadmap phase or NONE — PROJECT COMPLETE>

## Completed this session
- <compact list; do not accumulate prior-session history>

## Verification evidence
- `<check>` → <result>

## Current working state
<RUNNABLE / GREEN | KNOWN BROKEN / RECOVERABLE | BLOCKED>

When the state is `KNOWN BROKEN / RECOVERABLE` or `BLOCKED`, replace the placeholder with the
exact state and add both fields below. Runtime Audit rejects a declared non-runnable state without
them; do not imply success that was not observed.

- Why: <exact observed issue, dependency, or decision>
- First recovery action: <one concrete action>

## Blockers / uncertainty
- <none or exact issue>

## Next action
<one unresolved execution target only>

If the current task, acceptance criterion, manual verification, blocker, or other gate is still unresolved, keep this action focused on closing that gate. Do not name or describe later queued work here.

## Active task prompt
<root-relative docs/phases/<current-phase-name>.prompts.md#task-id, or NONE when no target remains>

Use the Phase-owned record for the same single target as Next action. Check freshness before
execution using `docs/system/CONTEXT_PROTOCOL.md`; do not bundle a second queued target.
Do not load historical prompts, full completed phases, completion reports, or chat history unless a specific contradiction requires them.
