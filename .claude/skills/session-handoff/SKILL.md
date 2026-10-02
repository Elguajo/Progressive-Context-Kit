---
name: session-handoff
description: End of a meaningful implementation/review session or phase transition.
activation: automatic
requires: ["docs/system/HANDOFF_PROTOCOL.md"]
---

# Session Handoff

Read current acceptance evidence and `docs/system/HANDOFF_PROTOCOL.md`. Classify the
session as `IN PROGRESS`, `PHASE COMPLETE`, or `PROJECT COMPLETE`. On `PHASE COMPLETE`,
update canonical owners first, write the durable phase completion report, then write the
completed phase's compact `## Completion Record` pointing to that report before updating
Roadmap markers. Retain Phase-owned task requests/prompts and observed outcome/evidence;
reference their IDs in the report. Update NEXT_SESSION only when hot navigation/state changes,
using an Active task prompt pointer instead of an editable executable prompt.

The phase completion report may preserve evidence-bounded technical detail useful to humans
or later investigation. The Completion Record must remain small enough for normal progressive
warm-up and must not duplicate the report. Legacy completed phases that predate separate
completion reports remain valid and do not require automatic migration.

For a safe mid-work pause, remain `IN PROGRESS`: finish the current atomic unit or return it to a
known recoverable state, start no queued unit, and record only actual disk/project state plus
observed verification. State whether it is `RUNNABLE / GREEN`, `KNOWN BROKEN / RECOVERABLE` (with
the exact issue and first recovery action), or `BLOCKED`. Do not fabricate completion artifacts,
create another ledger, or require a WIP Git commit.

For a non-trivial task inside an active phase, preserve its request/prompt, freshness checks,
observed result/evidence and relevant decisions/issues in its Phase-owned archive record. Keep the same
ID for unchanged instructions; changed instructions require a replacement revision linked to
the retained old record. Do not create one completion file per routine task.

Use Single-Focus Continuation for `NEXT_SESSION`: one handoff prompt = one unresolved
execution target. If the current task, acceptance criterion, manual verification, blocker, or
other gate remains open, both `Next action` and the referenced Phase prompt must focus only on closing
that target. Do not name or preload the next queued task/phase with wording such as "then
continue" or "after that start". Multiple substeps are allowed only when they all complete the
same target and share one acceptance boundary. Select later work only after the current target
is genuinely complete and its evidence/state has been persisted.

On a cold-start continuation, treat `NEXT_SESSION` as a pointer rather than authority. Reconcile
its target with the Roadmap/current Phase, live worktree/repository state, and decisive evidence
before acting. Apply the freshness check in `docs/system/CONTEXT_PROTOCOL.md`, even for a
record previously marked CURRENT. Preserve stale prompts and revise navigation/instructions
when those sources contradict them; migrate legacy inline prompts only when continuing them.
Keep the check narrow: do not replay
completed work or mine chat/transcript history unless a specific contradiction requires cold
historical evidence.

Do not repeat the diff line by line, claim success beyond observed evidence, or ask for
post-hoc approval after a clean finish unless another risky step remains. Include the
short launch instruction pointing to the saved Phase task ID and requiring a freshness check
when the project continues; do not repeat the task prompt body. Never end a turn with only
"waiting for confirmation/next action is X" — persist state and provide the continuation
record pointer before yielding to the user.
