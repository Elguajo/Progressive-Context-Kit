---
name: documentation-governance
description: Material edits to durable governance/project documentation such as AGENTS, README, architecture/ownership docs, dependency/project maps, or decision logs.
---

# Documentation Governance

Before materially editing durable documentation such as `AGENTS.md`,
`AGENTS.override.md`, `TASKS.md`, `AI_CHANGELOG.md`, README files, architecture or
ownership docs, dependency/project maps, or decision logs, stop and ask for confirmation.

State before asking:
- which documents should change;
- why each change is needed;
- what implementation and validation already occurred;
- whether each update is required or recommended.

An explicit request to edit a named durable document counts as approval for that document
within the requested scope. Ask again only if the required edit materially exceeds that
scope. Local comments, docstrings, and narrowly affected usage examples need no separate
approval when required for accuracy.

After approval, update only the canonical owner of each fact/rule. Reference other docs
instead of duplicating project truth.
