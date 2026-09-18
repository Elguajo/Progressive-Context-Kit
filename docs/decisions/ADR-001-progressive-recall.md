# ADR-001 — Progressive Recall

Status: Accepted
Date: 2026-09-15

## Context

PCK needs a way to recover materially relevant non-canonical historical context without making
current repository evidence, canonical project state, or agent behavior depend on an external
tool's configuration, index, brand, hooks, or global settings. New installations may gain the
capability; existing installed runtimes must continue operating unchanged when it is absent.

## Decision

Design **Progressive Recall** as a PCK-owned capability, not an external-tool adapter. This ADR
sets the architecture and implementation boundaries; it does not add the capability yet.

- The agent autonomously decides whether recall is useful after checking canonical PCK state and
  current source. It may refresh or discard project-local recall artifacts without a separate
  user decision.
- Recall artifacts will be project-local under `.progressive/recall/`, explicitly
  non-canonical, and disposable. They must not modify agent instructions, global configuration,
  Git hooks, or other projects.
- Every result must identify its source pointer and freshness. Current filesystem/diff and the
  canonical Brief, Architecture, Roadmap, Phase, ADRs, and acceptance evidence remain
  authoritative.
- Recall records may preserve compact pointers to canonical decisions or historical code areas;
  they must not create a parallel project-state, decision, or handoff store.
- The first implementation supports new runtimes only. Its capability marker/schema is created on
  fresh installation; framework updates leave existing runtimes unchanged. Runtime audit validates
  recall only when that marker declares it available.

## Implementation plan

1. Define the capability marker, project-local schema, retention/deletion behavior, source
   pointers, and freshness semantics. Add a versioned migration policy only if supporting legacy
   runtimes becomes a product requirement.
2. Implement bounded read/write operations with provenance and deterministic deletion. Validate
   that canonical state and uncommitted filesystem changes always override recall results.
3. Add new-runtime installation and capability-aware audit coverage; prove that an older runtime
   without the marker still passes its audit and receives no recall behavior.
4. Run controlled agent evaluations against the existing workflow: same repository snapshot,
   task wording, permissions, and acceptance criteria; promote only if quality is non-inferior
   and the measured cost per successful task improves.

## Consequences

- Positive: recall can evolve with PCK's ownership and safety model, while agents remain
  autonomous within a project-local boundary.
- Cost/risk: this is a new capability with storage, freshness, privacy, evaluation, and
  compatibility work; no token-saving or quality claim is implied before measurement.
- Revisit when: the capability schema, implementation evidence, and controlled evaluation results
  are available, or when legacy-runtime support becomes a stated product requirement.
