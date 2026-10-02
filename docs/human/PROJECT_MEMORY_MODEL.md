# Project Memory Model

> **Human-only documentation.** Framework Source only; excluded from Project Runtime.
>
> Russian: [`PROJECT_MEMORY_MODEL.ru.md`](PROJECT_MEMORY_MODEL.ru.md)

Progressive Context works best when each durable fact has one canonical owner.

Visual map: [`../visuals/project-memory-model.md`](../visuals/project-memory-model.md)

## Document responsibilities

### `PROJECT_BRIEF.md`
Answers: **What are we building, for whom, under what constraints, and how do we know it succeeds?**

It owns product intent and scope, not implementation history.

### `ARCHITECTURE.md`
Answers: **How does the system currently work?**

It owns current stack, system shape, trust boundaries, important integrations, and operational assumptions.

### `ROADMAP.md`
Answers: **What order are we building in, and what phase is current?**

It owns phase sequence and status, not task-level implementation detail.

### Current Phase
Answers: **What are we doing now, what are the acceptance criteria, and how will this phase be verified?**

It owns the plan/acceptance and an adjacent `<phase-name>.prompts.md` archive: original requests, preserved task prompts with IDs, revisions, freshness checks and observed outcomes/evidence. Changed instructions create a linked replacement revision. Only the active execution view enters normal context; original requests and accumulated evidence stay cold.

### `Completion Record`
Answers: **What must the next phase know without reading the full prior phase?**

It is intentionally compact and serves as the cross-phase bridge.

### Phase Completion Report
Answers: **What actually happened in the completed phase in enough detail for later investigation?**

It is durable cold history. It should not compete with Brief, Architecture, Roadmap, or ADRs as current truth.

### ADR
Answers: **Why was one consequential decision made?**

Use ADRs for rationale that needs to survive independently of one phase.

### `NEXT_SESSION.md`
Answers: **What should the next session know and do immediately?**

It is volatile hot navigation with an `Active task prompt` pointer into the Phase. Update it when state/navigation changes; executable task prompts are preserved in the Phase. Before execution, reconcile the record with the current phase, code, acceptance, blockers and authorization, even if it was previously marked CURRENT.

## Ownership rule

When a fact changes, update its canonical owner first.

Examples:

- system shape changed → update `ARCHITECTURE.md`;
- phase completed → write the Phase Completion Report and compact `Completion Record`;
- consequential architecture decision needs rationale → write/update an ADR;
- next action changed → overwrite `NEXT_SESSION.md`.

Do not solve uncertainty by copying the same durable fact into multiple documents.

For the upstream comparison and measured context-isolation fixture, see
[Task Continuity and Context Economy](TASK_CONTEXT_PRACTICES.md).
