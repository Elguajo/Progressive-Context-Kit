# Token / Context Budgets — Quality-First v1.9.0

Budgets prevent accidental bloat. They never authorize deleting behavior or preferred-tool routing needed for a correct, secure, complete engineering decision.

## Hard budgets

- Codex Personal global `global/AGENTS.codex.md`: **5,500 characters**.
- Claude Personal global `global/CLAUDE.md`: **5,500 characters**.
- Personal repo router `profiles/personal/AGENTS.md`: **3,600 characters**.
- Combined Codex Personal always-loaded layers: **9,100 characters**.
- Combined Claude Personal always-loaded layers: **9,100 characters**.
- Standalone composed `AGENTS.md`: **9,300 characters**.
- Canonical project read set (Brief + Architecture + Roadmap + current Phase + immediate prior Completion Record when present): soft **22,000 characters**.

v1.5 keeps the v1.4 quality-first routing model and context budgets unchanged. It adds no new normal startup layer: the compact immediate-previous-phase Completion Record bridge remains the only continuity addition beyond the v1.3 routing model. User-level global files remain bounded and are not copied into the Personal repository router.

`LINEAGE.md`, integration adapters, contracts, eval corpora, completed phases, and installed Skills are **not** normal warm-up context and do not consume model context merely because they exist in the repository.

## Optimization order

1. remove exact/near duplication within the same agent path;
2. replace copied procedures with canonical references;
3. move conditional long procedures to Skills/protocols/adapters;
4. use the context compiler/manifest instead of broad recursive reads;
5. remove stale historical narrative;
6. split unrelated phase work;
7. simplify wording without deleting semantics.

Agent-specific global files may intentionally mirror the same universal behavior because Codex and Claude load different user-level instruction locations. They are alternative deployment adapters, not simultaneous context for one agent.

Never delete an inherited Behavior Contract rule, Framework Contract rule, explicit user constraint, security boundary, acceptance criterion, materially useful preferred-tool route, debugging evidence, or validation requirement merely to hit a budget.
