# Framework Change Control

Framework-owned: root adapters, `global/`, `profiles/`, skills, prompts, templates,
`docs/system/`, `docs/contracts/`, migration/eval docs, integrations, and tools.

Project-owned after initialization: `docs/project/*`, `docs/phases/*`, `docs/decisions/*`,
application code/tests/migrations/configuration.

Framework updates must preserve project-owned state. Run audit/tests after changes.

## Structural promotion

For a recurring workflow correction, choose the strongest low-context enforcement layer before
adding prose. Evaluate in this order:

1. make the invalid state structurally impossible with a schema, canonical format, type,
   ownership contract, or invariant;
2. detect the failure deterministically with a validator, audit, gate, or integrity check;
3. make the correct path canonical mechanically with a compiler, generator, helper, or router;
4. use a conditional Skill, cold protocol, or on-demand reference when a procedure is needed;
5. use prose only for judgment that cannot be encoded.

Prefer an equally strong structural mechanism over repeated prose: it reduces behavioral
ambiguity and repeated active-context cost. Keep the fact/rule at one canonical owner; do not
create a contract for incidental wording or duplicate the policy across always-loaded layers.

## Architecture boundaries

PCK owns context, durable project state, continuity, and planning contracts. It must not acquire a
second workflow router, transcript-first resume dependency, persistent decision/execution ledger,
multi-agent scheduler, product verification harness, or autonomous shipping, PR landing, or
auto-merge behavior. Chat/transcript material is optional cold forensic evidence only. Product
surface verification remains in the execution layer; Roadmap, Phase, Completion Record/Report,
ADR, and volatile `NEXT_SESSION.md` retain their existing ownership boundaries.
