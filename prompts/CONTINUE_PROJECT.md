# Continue Project

Read only the repo Default Read Set. Check worktree state, resolve the one `[>]` phase,
use the immediate predecessor's Completion Record bridge when present, retrieve only evidence
needed for current acceptance criteria, resolve the Phase-owned task prompt pointer in NEXT_SESSION and apply the freshness check
in `docs/system/CONTEXT_PROTOCOL.md` before execution (or reconcile/migrate a legacy inline
prompt using `docs/system/HANDOFF_PROTOCOL.md`), load triggered skills only, implement autonomously,
and validate relevant behavior.

At handoff, persist a completed phase's durable Completion Record before moving the Roadmap
marker, retain task prompt/outcome records in their owning Phase, then update NEXT_SESSION
with only current hot state and the next active task prompt pointer. Keep unchanged prompt IDs
across pauses; do not rewrite executed prompt bodies or preload prompt history.

If all phases are `[x]`, route new requirements through change-request mode.
