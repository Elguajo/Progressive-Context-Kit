# Context Protocol

Use the smallest evidence set that can preserve correctness.

Normal product work may use `python3 tools/context_compile.py` to deterministically assemble a compact bundle from Brief, Architecture, Roadmap, current Phase plan and only the active task execution view, the immediate predecessor's `Completion Record` when present, and optional `CONTEXT_MANIFEST.json` hints. The compiler output is disposable; canonical files remain source of truth.

The previous-phase bridge is deliberately narrow: include only `## Completion Record`, never the full completed phase by default. Older completed phases remain retrievable when current evidence, an ADR, a regression, or an explicit historical dependency requires them.

Do not automatically read full completed phases, every ADR, all system docs, LINEAGE, migration evidence, eval corpora, or every installed Skill/tool adapter. Load a Skill/protocol/integration adapter only when its trigger matches.

Manifest hints are not authority over code reality. If a required path is stale/missing, report it and ground in repository evidence rather than hallucinating.

## Resume integrity

`NEXT_SESSION.md` is a navigation pointer, not authority over current project state. On a
cold-start continuation, first read the normal Default Read Set, resolve the current phase from
the Roadmap, then reconcile the handoff target against the current Phase, live worktree/repository
evidence, and only the verification or blocker evidence that determines whether the target remains
open. Continue it when those sources agree; when they contradict it, preserve the stale prompt and update navigation from the
canonical/live state and select the nearest unresolved target instead.

This reconciliation is deliberately narrow: do not replay completed work merely to verify it from
scratch, and do not warm up full completed phases, completion reports, or chat/transcript history
unless the contradiction creates a specific historical ambiguity that those sources can resolve.

## Task prompt freshness

Before executing a saved task prompt (including one explicitly supplied by ID), check:

1. **Authority and target:** active instruction layers and current user direction; Roadmap phase;
   referenced task/acceptance gate; prompt status and replacement links. Completed, cancelled or
   superseded records are history, not an instruction to run again. Work from another phase needs
   reconciliation/change routing, not silent replay.
2. **Scope and assumptions:** compare prompt intent/non-goals/acceptance with the current Phase,
   relevant Brief/Architecture/ADR constraints, dependencies and blockers. Detect changed APIs,
   missing prerequisites and incompatible assumptions only where they affect this target.
3. **Live progress and evidence:** inspect relevant worktree/code/tests and decisive verification
   or blocker evidence. Preserve unrelated changes. Identify what is already satisfied, still open,
   stale or broken; do not repeat completed work just because the old prompt names it.
4. **Authorization and verification:** verify any required approval still covers the actual action,
   and that checks/acceptance remain applicable. A saved prompt cannot override current safety
   boundaries or confer approval for new external writes/destructive actions.

Record the decision and its evidence in the Phase-owned record before dependent execution. CURRENT
means the authorized target remains applicable; execute only its unresolved portion. STALE
means changed instructions/state require reconciliation and, when needed, a replacement revision.
BLOCKED sets task Status to BLOCKED (not a Freshness value) for a missing dependency/decision/approval: preserve the target with its first recovery
action and proceed only with independent authorized work. If evidence already satisfies the
boundary, persist the completion rather than running the task again. A stored CURRENT must
be rechecked on each resume and after a material state/direction change; timestamps, commit
hashes and Runtime Audit alone do not establish semantic freshness.

The compiler loads the Phase plan and only the execution view of the record selected by
`NEXT_SESSION`: task/status/revision metadata, full Prompt, latest Freshness check and Current
checkpoint. The adjacent per-phase archive, original Request and accumulated Outcome / evidence
remain cold. Legacy inline history is excluded too. Oversized prompts become explicit pointers,
never truncated instructions; oversized checkpoints become targeted section pointers. Runtime Audit checks pointer ownership,
ID uniqueness, declared status/freshness and non-empty prompt; it cannot prove semantic
applicability. If a pointer is invalid or stale, select from canonical state before execution;
never silently load another historical prompt. Manual fallback reads the Phase plan and only
that selected record, not the whole prompt archive. See `docs/system/HANDOFF_PROTOCOL.md` for
record lifecycle, revision rules and legacy migration.

## Context economy

- On cold start or after context loss, use the normal compiled context. Within an already-grounded
  session, `python3 tools/context_compile.py --task-only` loads only the next task's execution view.
  It is not a substitute for instruction/Brief/Architecture/Phase constraints: reread affected
  canonical sections when direction/state changes, and the full read set after context loss.
- Do not duplicate canonical constraints or the task prompt in NEXT_SESSION, final responses,
  dispatch messages or completion reports. Carry paths/IDs and only task-specific deltas.
- Keep checkpoints short (normally at most 1200 characters); put detailed logs and prior results
  in cold evidence with a reference. The execution view inline ceiling is 4000 characters by
  default, using the existing compiler limit; required instructions are never silently cut.
- The compiler deduplicates already included manifest paths and keeps prompt archives as pointers.
  Do not read an entire archive to resolve one ID. Original request/details are retrieved only for
  a concrete ambiguity; resolved targets and superseded prompts never enter normal warm-up.
- Budget characters as a reproducible proxy, not an exact token count. A smaller window footprint
  does not by itself prove lower billing or better model accuracy. Measure representative bundles
  with the same canonical constraints/acceptance before claiming savings.
