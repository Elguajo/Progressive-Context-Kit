---
name: session-handoff
description: End of a meaningful implementation/review session or phase transition.
---

# Session Handoff

Read current acceptance evidence and `docs/system/HANDOFF_PROTOCOL.md`. Classify the
session as `IN PROGRESS`, `PHASE COMPLETE`, or `PROJECT COMPLETE`. On `PHASE COMPLETE`,
write the completed phase's durable `## Completion Record` first, then update Roadmap markers
consistently. Overwrite NEXT_SESSION as volatile hot navigation rather than preserving old
handoffs or turning it into a second specification.

The completion report must remain concise and evidence-bounded:
- **Implemented:** what changed and which approved direction was used.
- **Files changed:** each relevant file and its purpose.
- **Validation:** commands/checks actually run and their results.
- **Important decisions:** only meaningful architecture, compatibility, security, or data decisions.
- **Remaining risks:** unresolved assumptions/follow-ups; omit when none.

Do not repeat the diff line by line, claim success beyond observed evidence, or ask for
post-hoc approval after a clean finish unless another risky step remains. Include the
ready-to-copy next-session prompt when the project continues. Never end a turn with only
"waiting for confirmation/next action is X" — persist state and provide the continuation
prompt before yielding to the user.
