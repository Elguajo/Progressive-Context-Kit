# Next Session

> Volatile hot context. Overwrite this file on each meaningful handoff. Durable completed-phase history belongs in `docs/completions/` with only a compact bridge in the completed phase `Completion Record`.

Outcome: <IN PROGRESS | PHASE COMPLETE | PROJECT COMPLETE>

## Current phase
<exact Roadmap phase or NONE — PROJECT COMPLETE>

## Completed this session
- <compact list; do not accumulate prior-session history>

## Verification evidence
- `<check>` → <result>

## Blockers / uncertainty
- <none or exact issue>

## Next action
<one unresolved execution target only>

If the current task, acceptance criterion, manual verification, blocker, or other gate is still unresolved, keep this action focused on closing that gate. Do not name or describe later queued work here.

## NEXT SESSION PROMPT
```text
Continue only: <same single unresolved execution target as "Next action" above>

Finish and persist evidence for this target before selecting any later task or phase work.
Substeps needed to complete this same target are allowed, but do not bundle a second queued
execution target into this handoff. Do not use "then continue/start/implement <later task>"
while this target remains unresolved.

Read the active instruction layers, recover project state from the Default Read Set,
verify the Roadmap marker, and continue this one target autonomously. Do not reread
full completed phases, completion reports, or chat history unless evidence requires it.
```
