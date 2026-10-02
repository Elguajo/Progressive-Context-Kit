# Handoff Protocol

Classify the session `IN PROGRESS`, `PHASE COMPLETE`, or `PROJECT COMPLETE`.
Roadmap stays canonical for phase status.

## Phase completion transaction

When a phase satisfies its acceptance criteria:

1. update Architecture/ADR/other canonical owners first when system shape or a consequential decision changed;
2. reconcile task records with observed acceptance evidence and retain their requests/prompts/outcomes in the completed Phase; unresolved required work prevents phase completion;
3. write the durable phase report under `docs/completions/<phase-name>.md` using `templates/PHASE_COMPLETION.template.md`, referencing task IDs without copying their bodies;
4. persist a compact `## Completion Record` in the completed phase **before moving the Roadmap marker**. It should point to the final report and keep only the small cross-phase bridge needed for progressive context;
5. mark the completed phase `[x]` and exactly one next phase `[>]` when one exists;
6. select one next unresolved target, create its Phase-owned prompt record, and overwrite `NEXT_SESSION.md` in place with hot navigation plus that record pointer (or `NONE` on project completion).

The phase completion report is durable human-readable history. Capture evidence-bounded detail that would otherwise bloat hot context:
- **Outcome / Delivered** — capabilities and artifacts that now exist;
- **Implementation notes** — durable technical facts worth preserving, not a diff diary;
- **Decisions made** — consequences plus ADR/canonical references when applicable;
- **Deviations / technical debt** — gaps surviving completion;
- **Problems discovered** — durable issues/workarounds worth remembering;
- **Verification evidence** — checks actually observed and results;
- **Architectural impact / Follow-up** — what later phases may rely on and explicit later work.

A Completion Record remains compact durable routing history. Capture only:
- **Status / Completed** — completion state/date when useful;
- **Final report** — relative path to the phase completion report when one exists;
- **Outcome** — one concise result;
- **Validation summary** — only the evidence needed to trust the transition;
- **Decisions / Technical Debt affecting later phases** — concise consequences;
- **Handoff to Next Phase** — assumptions/capabilities the next phase may safely rely on.

Do not duplicate the full completion report inside the Completion Record. Normal warm-up reads only the compact Completion Record; the detailed report is read on demand when investigation, audit, or historical context requires it.

Backward compatibility: completed phases created before phase completion reports existed remain valid with only their existing `## Completion Record`. Do not force migrations merely to satisfy the new convention. Add a report retroactively only when its durable detail is materially useful.

For non-trivial tasks inside an active phase, preserve request/prompt and outcome/evidence in the Phase-owned task prompt record described below. A compact Task Completion note may link that record when later work needs it; avoid duplicate evidence. Do not create one completion file per routine task.

If the session remains `IN PROGRESS`, keep the phase active and do not fabricate a phase completion report or completion record.

On project completion every phase is `[x]` and none is `[>]`.

## Safe pause transaction

A safe pause is an `IN PROGRESS` handoff, never a fourth session outcome. Before pausing, finish
the current atomic unit or return it to a known recoverable state; do not begin another queued
unit. Record only facts actually present on disk or in canonical project state, verification
actually observed, and one of these working states:

- `RUNNABLE / GREEN`;
- `KNOWN BROKEN / RECOVERABLE` with the exact observed issue and first recovery action; or
- `BLOCKED` with the exact external dependency or decision.

For either non-runnable state, use these exact `NEXT_SESSION` fields so a Runtime Audit can catch
a dangerous false handoff: `- Why: <non-empty fact>` and `- First recovery action: <one concrete
action>`. This lint checks declared state only; it does not decide whether an agent's semantic
claim of completion is true.

Persist an Architecture, current-Phase, or ADR update only when its canonical fact actually
changed. Then update `NEXT_SESSION.md` with one resume target, its Phase-owned prompt pointer and first concrete action only when navigation/state changes. Keep the same prompt ID for unchanged instructions across pauses; append observed evidence/recovery information to its record.
Do not fabricate a completion record/report, create another durable execution ledger, or require
a WIP Git commit: Git may help where a project convention already uses it, but safe pause also
works without Git.

## Phase-owned task prompts

Each meaningful execution target gets a Phase-owned record in one adjacent archive:
`docs/phases/<phase-name>.prompts.md`, under `## Task prompts`, using
`templates/TASK_PROMPT.template.md`. The phase plan keeps only a pointer; never inline the
archive into its acceptance/execution plan. One archive per phase avoids one file per tiny task. A target is a cohesive task or acceptance/recovery
gate, not every mechanical substep. Give it a phase-local unique ID such as `task-01-r1` and
reference it as a root-relative archive path plus `#task-01-r1`. Create it when selecting that
target and set NEXT_SESSION's active pointer before executing it; do not generate a backlog
of speculative future prompts. Keep section/record headings outside fenced text. Fence
original request and prompt bodies (use a longer fence if the body itself contains fences)
so embedded Markdown headings cannot be mistaken for record boundaries.

Preserve the original request and executed prompt body after use. If only a summary is
available, label it as a summary; never invent a verbatim request or recover it by mining chat.
Omit secrets/private payloads and use safe references when the original contains them. The
record preserves intent, not new authorization: old approval cannot authorize a newly risky step.

Status is `READY`, `IN PROGRESS`, `BLOCKED`, `COMPLETED`, `SUPERSEDED`, or `CANCELLED`.
Freshness is `UNCHECKED`, `CURRENT`, or `STALE`; it describes the last check, not a timeless
permission to execute. Keep the latest decisive freshness check and a compact `Current checkpoint` in the same
record; update these in place without accumulating routine check entries. Append only material
observed outcomes/deviations/recovery evidence under `Outcome / evidence`; this history is cold. Update status and append evidence without rewriting the executed request/prompt.
Unchanged tasks retain their ID across sessions; a changed scope, acceptance boundary or
execution instruction gets a new revision with `Supersedes: <old-id>`. Mark the old record
`SUPERSEDED` and link the replacement; retain its partial result/evidence. Cancel abandoned
work explicitly. Mark `COMPLETED` only after the task acceptance boundary is verified; prompt
text alone is never evidence that the work happened.

Before every execution/resume, apply the freshness check in `docs/system/CONTEXT_PROTOCOL.md`.
If the request is still valid, continue only the unresolved portion without rewriting the prompt
or redoing accepted work. If stale, preserve it, reconcile canonical state, then create a corrected
record only for a still-authorized target. If blocked, keep the unresolved target and exact recovery
action. Missing authorization or a material user-only choice requires clarification; ordinary
staleness with an evident authorized correction does not.

## NEXT_SESSION semantics

`NEXT_SESSION.md` is volatile hot navigation, not project history. Update it in place when
navigation/state changes; do not create accumulating `NEXT_SESSION_001.md` files. It contains
current phase, a compact session result, verification, working state, blockers, next action and
`## Active task prompt` with the Phase-owned record reference. It must not contain a second
editable executable task prompt. The final response may provide a short launch instruction
pointing to this record and requiring a freshness check; do not duplicate its body.

On resume, treat that handoff as a pointer. Reconcile its target with the Roadmap/current Phase,
the live worktree/repository, and decisive evidence before acting. A stale handoff must not override canonical state.
This is a bounded check, not a request to reconstruct work from chat history or re-audit completed work.

Legacy inline Phase records remain readable, but do not keep both inline and archive copies.
Do not automatically move existing records; newly created records use the adjacent archive.
Legacy projects with only a `NEXT SESSION PROMPT` remain readable. On the next meaningful
continuation, reconcile it first, preserve the available prompt as a Phase-owned archive record with source
`legacy NEXT_SESSION`, then replace the executable block with the record pointer. Do not invent
missing history, migrate completed phases, or create task records in an uninitialized project.
Framework updates preserve project-owned Phase records and NEXT_SESSION; they never migrate
or overwrite this history automatically. With no active target, use `NONE`.

### Single-focus continuation

One handoff prompt = one unresolved execution target.

Select the nearest unfinished target from canonical project state in this order:

1. unresolved blocker, manual verification, acceptance criterion, or other gate on the current work;
2. otherwise, the unfinished current task;
3. only after that target is complete and its evidence/state is persisted, the next task may become the new target;
4. only after the phase completion transaction is complete may work from the next phase become the new target.

If a current target is unresolved, `## Next action` and the referenced Phase-owned prompt must focus only on closing it. Do not name, describe, preview, or preload later queued tasks or phases in the handoff prompt. In particular, do not write transitions such as `then continue Task N+1`, `after that start ...`, or equivalent wording while the current target remains open.

Several concrete substeps are allowed only when they share one acceptance boundary and are all necessary to finish the same target, for example `apply fix → run targeted verification → persist evidence`. That is still one execution target. `finish current task → start next task` is two targets and must be split across state transitions.

Once the current target is genuinely complete and evidence is persisted, normal workflow may select the next target from the Phase/Roadmap. The previous handoff must not pre-plan or bundle that future target merely because it is already visible in canonical planning documents.
