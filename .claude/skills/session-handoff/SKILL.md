---
name: session-handoff
description: End of a meaningful implementation/review session or phase transition.
---

# Session Handoff

Read current acceptance evidence and `docs/system/HANDOFF_PROTOCOL.md`. Classify the
session as `IN PROGRESS`, `PHASE COMPLETE`, or `PROJECT COMPLETE`. On `PHASE COMPLETE`,
update canonical owners first, write the durable phase completion report, then write the
completed phase's compact `## Completion Record` pointing to that report before updating
Roadmap markers. Overwrite NEXT_SESSION as volatile hot navigation rather than preserving
old handoffs or turning it into a second specification.

The phase completion report may preserve evidence-bounded technical detail useful to humans
or later investigation. The Completion Record must remain small enough for normal progressive
warm-up and must not duplicate the report. Legacy completed phases that predate separate
completion reports remain valid and do not require automatic migration.

For a non-trivial completed task inside an active phase, preserve only a compact task result,
evidence, and decisions/issues in the phase file when later work needs them. Do not create one
completion file per routine task.

Do not repeat the diff line by line, claim success beyond observed evidence, or ask for
post-hoc approval after a clean finish unless another risky step remains. Include the
ready-to-copy next-session prompt when the project continues. Never end a turn with only
"waiting for confirmation/next action is X" — persist state and provide the continuation
prompt before yielding to the user.
