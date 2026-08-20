# Codex Custom Instructions v2.5 — Progressive-aware migration

This note records the architectural split used to migrate the reviewed Codex Custom Instructions
v2.4 into Progressive Context Kit. It does not duplicate the canonical instruction text; the
canonical Codex universal contract remains `global/AGENTS.codex.md`.

## Goal

Keep only universal engineering guarantees always loaded while moving task-specific procedures
into Progressive routing, Skills, and protocols.

> **Minimize always-loaded behavior, not available behavior.**

This is the behavior-side counterpart to:

> **Minimize active context, not available knowledge.**

## v2.4 → v2.5 ownership

| v2.4 concern | v2.5 canonical owner |
|---|---|
| Role / language / communication baseline | `global/AGENTS.codex.md` |
| Task classification / autonomy threshold | `global/AGENTS.codex.md` |
| Repository grounding | `global/AGENTS.codex.md` |
| Universal engineering invariants | `global/AGENTS.codex.md` |
| Detailed testing policy | `.agents/skills/implementation-execution/SKILL.md` |
| Material architecture decision workflow | `.agents/skills/architecture-decision/SKILL.md` |
| Code review procedure | `.agents/skills/code-review/SKILL.md` |
| Implementation / bug-fix execution | `.agents/skills/implementation-execution/SKILL.md` |
| Validation loop | `docs/system/QUALITY_PROTOCOL.md` |
| Security detail | global approval boundary + `.agents/skills/security-sensitive-change/SKILL.md` |
| Detailed documentation governance | `.agents/skills/documentation-governance/SKILL.md` |
| Final report / Action-First output | `global/AGENTS.codex.md` |

The global layer keeps only short routing/invariant statements for testing and documentation;
it does not duplicate their task-specific procedures.

## Adopted v2.4 improvements

- Architecture decisions no longer force exactly three A/B/C strategies; they show all and only
  materially different viable options.
- Substantial testable work may add a lightweight development-only test framework autonomously
  when repository evidence supports it and scope/maintenance/production dependencies stay bounded.
- Implementation-coupled README usage/setup, API examples, configuration docs, comments, and
  docstrings update automatically; durable governance/policy/decision records remain approval-gated.
- Completion reporting is result-first: `Result`, optional `Manual check`, `Files changed`,
  `Validation`, `Important decisions`, optional `Remaining risks`.

The first three detailed procedures above live in Progressive Skills/protocols rather than the
always-loaded global adapter.

## Preserved Progressive guarantees

v2.5 retains the existing Execution Efficiency rules instead of replacing them with the older
v2.4 grounding text: batch independent reconnaissance, smallest-sufficient inspection, grouped
environment probing, convergent validation, repeated-failure pivot, and bounded polling.
Efficiency never overrides correctness, safety, acceptance criteria, required validation,
project-state updates, or completion/handoff.

## Current context sizes

Deterministic Unicode-character counts after final cleanup:

- Codex universal core: **5,176** characters;
- Claude universal core: **5,228** characters;
- Personal repository router: **3,552** characters;
- Codex Personal always-loaded composition: **8,728** characters;
- Claude Personal always-loaded composition: **8,780** characters;
- Standalone generated composition: **8,909** characters.

Global adapter regression budgets are **5,500 characters** each. Task Skills and cold protocols
remain conditional rather than part of normal warm-up.

## Protection

Framework rules `FW-054`–`FW-060`, static scenario `progressive-aware-universal-v2-5`, profile
tests, and `test_progressive_aware_v25.py` protect the split. Profile tests explicitly reject
reintroduction of detailed Testing/Documentation procedures into the global adapters. Historical
Behavior Contract evidence is not rewritten; v2.5 is a new Progressive-aware architecture layer.
