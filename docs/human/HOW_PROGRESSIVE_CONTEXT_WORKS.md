# How Progressive Context Works

> **Human-only documentation.** Framework Source only; excluded from Project Runtime.
>
> Russian: [`HOW_PROGRESSIVE_CONTEXT_WORKS.ru.md`](HOW_PROGRESSIVE_CONTEXT_WORKS.ru.md)

Progressive Context Kit is built around one rule:

> **Minimize active context, not available knowledge.**

The goal is not to make the project know less. The goal is to stop every fresh AI session from loading everything the project has ever known.

## The basic model

See: [`../visuals/progressive-context-overview.md`](../visuals/progressive-context-overview.md)

Project knowledge is split conceptually into two groups:

- **active / hot context** — the smallest set needed to understand the product, current system, current phase, and immediate task;
- **cold / on-demand context** — detailed history and evidence that remains available but is read only when needed.

A normal session should recover roughly:

```text
repository behavior
→ PROJECT_BRIEF
→ ARCHITECTURE
→ ROADMAP
→ current Phase
→ previous compact Completion Record when relevant
→ relevant code/tests + matching Skill
```

It should not recursively read every completed phase, ADR, completion report, human guide, or framework-development file.

## Fresh-session flow

See: [`../visuals/session-context-flow.md`](../visuals/session-context-flow.md)

A fresh session first reconstructs the minimum reliable state, then expands context only when the task requires evidence that is not already in the active set.

This gives two useful properties at the same time:

1. continuity does not depend on chat history;
2. historical knowledge is not destroyed just to save tokens.

## Why completion history is cold

A completed phase may have a detailed Phase Completion Report, but normal continuation uses only its compact `Completion Record` as the cross-phase bridge.

If a later task needs exact implementation history, the agent can follow the report pointer and read that specific report on demand.

## Why this is not just summarization

Progressive Context is also an ownership and routing model. Different documents answer different questions, and workflows load different Skills depending on the task.

See:

- [`PROJECT_MEMORY_MODEL.md`](PROJECT_MEMORY_MODEL.md)
- [`../visuals/tool-routing.md`](../visuals/tool-routing.md)

## Failure modes this model tries to prevent

- reading the whole repository before every task;
- treating old plans as current truth;
- accumulating session history forever in `NEXT_SESSION`;
- duplicating architecture across multiple documents;
- loading every installed Skill for every task;
- losing useful historical evidence merely to keep context small.

The intended result is a project that can grow in available knowledge without making every session grow at the same rate.
