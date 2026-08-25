# Skill Activation Contract

Skill activation is declared in the YAML frontmatter of every canonical `.agents/skills/*/SKILL.md` file as:

```yaml
activation: automatic | explicit | both
```

The field describes **how the Skill may enter active behavior**, not whether a user is allowed to ask for the underlying capability.

- `automatic` — the repository router/model may activate the Skill when its task trigger matches. It is not a separately promoted user-facing orchestration entrypoint.
- `explicit` — the Skill must not be inferred as routine task behavior; activate it only for a direct user/maintainer request or a named entrypoint that intentionally invokes it.
- `both` — the Skill is intentionally supported both as automatic routed behavior and as an explicit orchestration entrypoint.

Current policy keeps existing routing semantics unchanged: router-driven product-work Skills are `automatic`; `workflow-audit` is `explicit` because framework/runtime integrity auditing is not part of ordinary product-task routing.

Canonical metadata lives only in `.agents/skills/`; `.claude/skills/` is a generated mirror. Adding an activation field must not move detailed Skill procedures into always-loaded instructions or increase the normal project context budget.

Router reachability, dangling routes, Skill dependencies, and orphan detection are enforced by the separate `docs/contracts/ROUTING_INTEGRITY.md` contract and `tools/routing_integrity.py` validator.
