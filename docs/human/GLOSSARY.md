# Progressive Context Kit — Glossary

> **Human-only reference.** This file belongs to Framework Source and is deliberately excluded from Project Runtime.
>
> Russian version: [`GLOSSARY.ru.md`](GLOSSARY.ru.md)

Use this page when a framework term, abbreviation, identifier, or project-memory concept is unfamiliar.

## Writing convention

For human-facing documentation, prefer the full term on first use and put the abbreviation in parentheses only when the abbreviation will actually be reused.

Good:

```text
Architecture Decision Record (ADR)
Default Read Set (DRS)
Phase Completion Report (PCR)
```

Avoid abbreviation-heavy prose such as:

```text
NSP must preserve DRS semantics after PCR.
```

Stable identifiers such as `PC-012`, code symbols, filenames, CLI flags, and compact diagram labels may remain short.

## Progressive Context Kit abbreviations

| Abbreviation | Meaning | Notes |
|---|---|---|
| **PC** | Progressive Context | Used formally in protected invariant IDs such as `PC-001` and `PC-012`. |
| **FW** | Framework | Informal shorthand. Prefer **Framework** in human documentation. |
| **FS** | Framework Source | Informal shorthand. Prefer the full name unless space is constrained. |
| **DRS** | Default Read Set | The smallest standard project-state set used to recover context before expanding on demand. Prefer the full term in normal prose. |
| **CR** | Completion Record | Compact durable bridge stored with a completed Phase. Prefer the full term in normal prose. |
| **PCR** | Phase Completion Report | Detailed durable history for one completed Phase. It is cold/on-demand context. Prefer the full term in normal prose. |
| **NS** | `NEXT_SESSION` | Informal shorthand for the volatile hot continuation state. Prefer the filename or full term. |
| **NSP** | `NEXT_SESSION_PROMPT` | Informal shorthand for the ready-to-copy single-focus continuation prompt. Prefer the full name. |

These abbreviations are not a requirement for using the Kit. They mainly help interpret implementation notes, issues, PR discussions, diagrams, and invariant IDs.

## Common engineering abbreviations

| Abbreviation | Meaning | In this project |
|---|---|---|
| **ADR** | Architecture Decision Record | Records one consequential architectural decision and its rationale. |
| **AC** | Acceptance Criteria | Conditions that must be satisfied before a Task or Phase is treated as complete. |
| **PR** | Pull Request | A proposed GitHub change reviewed/validated before merging. |
| **CI** | Continuous Integration | Automated checks such as contracts, audits, builds, and tests. |
| **QA** | Quality Assurance | Validation of correctness and user-visible behavior, including manual verification when required. |
| **CLI** | Command-Line Interface | Command-based interaction such as `python3 tools/build_release.py`. |
| **API** | Application Programming Interface | A programmatic interface between software components or services. |
| **SHA / SHA-256** | Secure Hash Algorithm / SHA-256 | Used for commit identifiers and release integrity checks. |
| **TDD** | Test-Driven Development | Implementation discipline where tests guide behavior changes when appropriate. |

## Core framework terms

### Framework Source

The canonical GitHub repository used to develop, test, document, migrate, and release Progressive Context Kit itself.

It contains framework-development material such as `docs/`, `templates/`, `tools/`, contracts, tests, profiles, and release tooling.

### Project Runtime

The generated minimal package placed inside a real product repository.

It contains the operational Progressive Context machinery needed by the agent, but intentionally excludes Framework Source-only human documentation and development material.

### Project-owned

State that belongs to the real product and must survive framework updates. Examples include project memory, phases, completion reports, decisions, application code, and project-specific instructions.

### Framework-owned

Runtime machinery generated from Framework Source and safe to update when the framework version changes, subject to the framework's preservation rules.

### Canonical owner / source of truth

The one document or artifact responsible for a durable fact or rule. Other documents may summarize or point to it, but should not become competing sources of truth.

### Default Read Set

The minimal standard context used to recover project state before loading more material. The exact operational routing is defined by the framework; the principle is to start small and expand only when evidence requires it.

### Hot context

Information needed immediately for the current continuation, such as current state and the nearest unresolved execution target.

### Cold / on-demand context

Available knowledge that should not be loaded during normal warm-up unless investigation, audit, history, or evidence requires it. Detailed Phase Completion Reports are an example.

### Always-loaded context

Instructions or context that are loaded by default for essentially every relevant session. Progressive Context Kit keeps this layer under explicit budgets.

### Progressive loading

Starting from the smallest sufficient context and loading additional files, history, skills, or evidence only when the current task requires them.

### Phase

A bounded implementation stage with a goal, tasks, acceptance criteria, and verification expectations.

### Task

A unit of work inside a Phase. Routine Tasks do not receive separate completion-report files.

### Acceptance criterion / acceptance gate

A condition that must be observed as satisfied before the relevant Task or Phase can be considered complete. An unresolved manual verification is still an open gate.

### Completion Record

A compact durable bridge left in a completed Phase. It preserves only the small amount of information later work needs during normal progressive warm-up.

### Phase Completion Report

A detailed durable report for one completed Phase. It stores implementation notes, decisions, deviations, verification evidence, and other history that would otherwise bloat hot context.

### `NEXT_SESSION`

Volatile hot navigation for the next meaningful continuation. It is overwritten rather than accumulated as history.

### `NEXT_SESSION_PROMPT`

The ready-to-copy continuation prompt inside `NEXT_SESSION`. Under **Single-Focus Continuation**, it carries one unresolved execution target only; later queued work remains in the Phase/Roadmap until the current target is actually closed and persisted.

### Handoff

The end-of-session state transition where the agent persists current evidence/state and prepares a safe continuation for the next session.

### Single-Focus Continuation

The rule that one handoff prompt carries one unresolved execution target. If the current Task, blocker, or acceptance gate is still open, the prompt focuses only on closing it and does not preload the next queued Task.

### Skill

A specialized workflow loaded when a task type requires it. Installed does not mean loaded, and loaded does not mean invoked for every task.

## Related guides

- [`GETTING_STARTED.md`](GETTING_STARTED.md)
- [`HOW_PROGRESSIVE_CONTEXT_WORKS.md`](HOW_PROGRESSIVE_CONTEXT_WORKS.md)
- [`PROJECT_MEMORY_MODEL.md`](PROJECT_MEMORY_MODEL.md)
- [`UPDATING_RUNTIME.md`](UPDATING_RUNTIME.md)
- [`../visuals/README.md`](../visuals/README.md)
