# Phase <NN> — <NAME>

## Goal
<single verifiable outcome>

## Context
<only phase-specific facts not canonical elsewhere>

## Context hints
<optional non-obvious files/ADRs/skills; keep empty when discovery is obvious and use CONTEXT_MANIFEST.json for machine routing>

## In scope
- <...>

## Out of scope
- <...>

## Tasks
- [ ] <cohesive task>

For a completed non-trivial task, keep any durable task result directly under the task or in a compact `Task Completion` note: Result; Evidence; Decisions/Issues only when they affect later work. Do not create one file per routine task.

## Task prompts
<pointer to docs/phases/<this-phase-name>.prompts.md — one adjacent archive per phase.
Append records there using templates/TASK_PROMPT.template.md, under ## Task prompts.
Use unique IDs such as task-01-r1; preserve request/prompt bodies and evidence after use.
NEXT_SESSION points to the current archive record. The compiler includes only its execution
view, never the archive, original request or accumulated evidence. Do not prewrite queued tasks.>

## Acceptance criteria
- [ ] <observable criterion>

## Negative / security cases
- <only when relevant>

## Verification
- <commands/manual checks/evidence required>

## Completion Record
<populate only when this phase becomes [x]. Keep this bridge compact: Status/Completed; Final report path when one exists; Outcome; Validation summary; Decisions/Technical Debt affecting the next phase; Handoff. Reference task prompt IDs when useful; never copy their bodies here. Detailed durable phase history belongs in the phase completion report under docs/completions/, not here. Legacy completed phases without a separate report remain valid.>
