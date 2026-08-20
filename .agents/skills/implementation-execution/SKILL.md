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

Before the first execution/build step, when several required runtime, dependency, compiler,
or tool prerequisites are already knowable, check them in one grouped probe instead of
discovering them one failure at a time. Resolve only confirmed missing prerequisites and
respect existing dependency/approval policy; do not install speculative packages or turn a
small task into environment setup. A later probe is justified only by new evidence from the
first execution.

Treat polling as a costed execution step. If a command is still running and the harness
returns control, wait in coarse intervals appropriate to the expected duration — normally at
least 30 seconds for builds or test suites — instead of repeatedly checking with short polls.
Do not send empty/no-op input only to peek, and do not poll at all when the execution call
already blocks until completion. Poll sooner only when the command is expected to finish
quickly or new evidence makes an earlier check useful.

For bug fixes: root cause → reproduce when practical → smallest complete fix → regression
test when supported → adjacent-behavior verification. Use `systematic-debugging` when the
cause is unclear rather than guessing.

After implementation, apply `docs/system/QUALITY_PROTOCOL.md` exactly. Do not mark work
complete before required evidence is reconciled with acceptance criteria.
