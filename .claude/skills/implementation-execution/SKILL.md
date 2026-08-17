---
name: implementation-execution
description: Non-trivial implementation after direction is clear, including feature work and complete bug-fix execution.
---

# Implementation Execution

Once direction is clear, implement end-to-end in one cohesive pass. Approval is for the
chosen direction, not for incomplete core-logic fragments.

A complete change includes all required integration points, imports, types, schemas,
configuration, critical edge cases/error handling, backward compatibility unless a break was
approved, and relevant tests when an existing framework exists. Leave no debug output, dead
code, placeholders, pseudo-code, or unnecessary dependencies. Follow repository conventions
and avoid unrelated changes.

For bug fixes: root cause → reproduce when practical → smallest complete fix → regression
test when supported → adjacent-behavior verification. Use `systematic-debugging` when the
cause is unclear rather than guessing.

After implementation, apply `docs/system/QUALITY_PROTOCOL.md` exactly. Do not mark work
complete before required evidence is reconciled with acceptance criteria.
