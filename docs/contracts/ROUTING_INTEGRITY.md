# Routing Integrity Contract

Routing integrity protects the link between the repository router, task-triggered Skills, and the local artifacts those Skills require.

The canonical Framework Source router is `profiles/personal/AGENTS.md`. Project Runtime checks the generated root `AGENTS.md`; no separate routing registry is introduced.

## Reachability

- Every `automatic` or `both` Skill must be reachable from the `## Workflow routing` section.
- Every routed Skill name must resolve to an installed canonical Skill.
- An `explicit` Skill is intentionally exempt from automatic reachability and must not appear as a routine automatic route.
- `workflow-audit` remains explicit-only unless its activation semantics are deliberately changed.

## Declared edges

Optional Skill frontmatter may declare existing relationships without changing behavior:

```yaml
requires: ["prompts/START_NEW_PROJECT.md", "docs/system/PLANNING_DEPTH.md"]
may_delegate: ["existing-project-adoption"]
```

- `requires` lists repository-local files the Skill directly depends on. Every path must exist.
- `may_delegate` lists Skills the current Skill may hand control to under its existing procedure. Every target must exist, must not be self-referential, and must allow automatic activation (`automatic` or `both`).
- Empty relationships are omitted rather than encoded as filler.

The Runtime builder transforms declared source paths together with the Skill text, so the same validator checks generated `.progressive/...` dependencies after release composition.

`tools/routing_integrity.py` is the executable contract. Source audit and Runtime audit both invoke it. The validator is Framework/Runtime maintenance evidence; it does not add detailed routing or dependency content to normal warm-up context.
