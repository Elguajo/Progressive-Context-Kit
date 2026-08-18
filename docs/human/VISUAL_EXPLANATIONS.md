# Visual Explanations

Human-only guidance for explaining Progressive Context Kit architecture in Framework Source.

> Human explanatory assets are source-only documentation and must never be required for Runtime operation or packaged into Project Runtime.

## Purpose

Use visual explanations when a diagram makes a framework concept faster to understand than prose alone. They explain canonical documentation; they do not become a second source of truth.

## Canonical ownership

Visuals may summarize or point to canonical owners such as:

- `docs/project/*` for project truth;
- `docs/system/*` for framework protocols and ownership rules;
- `docs/contracts/*` for protected framework behavior;
- code/tests for executable behavior.

If a visual disagrees with its canonical owner, the canonical owner wins and the visual must be updated.

## When to add a visual

Prefer a visual for:

- architecture and ownership relationships;
- lifecycle/state transitions;
- source → runtime → release pipelines;
- context routing and hot/cold boundaries;
- migration/update safety boundaries;
- decision flows with several branches.

Do not add a visual when a short paragraph or checklist is clearer.

## Format and placement

1. Prefer Mermaid in Markdown for diagrams rendered by GitHub.
2. Use compact ASCII only when it communicates the idea more clearly.
3. Keep one primary idea per diagram.
4. Keep labels short; put nuance in nearby prose.
5. Store detailed reusable human visual explanations under `docs/visuals/`.
6. A compact inline variant may appear in source-only `README*` or `docs/human/*` when seeing the diagram in place materially improves onboarding or comprehension.
7. Inline variants should stay simpler than the detailed visual and should link to the relevant human guide or `docs/visuals/` page rather than duplicating all explanatory text.
8. Do not add visual assets, visual indexes, or visual-only guidance to `AGENTS.md`, `CLAUDE.md`, agent Skills, runtime protocols, or normal context compilation.

## Runtime boundary

The Project Runtime must remain operational without human visual documentation.

`tools/runtime_layout.py` must not map `docs/visuals/` or human-only visual/conceptual guides into `.progressive/`.

Release tests must verify that human visual documentation is absent from the Runtime ZIP.
