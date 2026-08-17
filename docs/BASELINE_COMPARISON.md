# Baseline Comparison — v1.7.0 Deployment + Tooling

Counts use deterministic Unicode characters. `chars / 4` is rough intuition only, not exact tokenizer/billing output.

## Archived old Custom Instructions

- **11,540 characters**
- rough intuition: **~2,885 tokens**
- hash-pinned under `docs/migration/`

## Codex Personal always-loaded layers

- `global/AGENTS.codex.md`: **4,939 characters**
- `profiles/personal/AGENTS.md`: **3,561 characters**
- combined: **8,500 characters** (at the 8,500-char hard budget)
- rough intuition: **~2,125 tokens**
- reduction versus the old Custom Instructions **alone**: **26.3%**

## Claude Personal always-loaded layers

- `global/CLAUDE.md`: **4,995 characters**
- shared `profiles/personal/AGENTS.md`: **3,561 characters**
- combined: **8,556 characters**
- rough intuition: **~2,139 tokens**
- reduction versus the old Custom Instructions **alone**: **25.9%**

Project `CLAUDE.md` imports only the active root `@AGENTS.md`; it does not import Standalone directly in Personal mode. This prevents a second copy of universal behavior from entering Claude startup context.

## Standalone

- composed root `AGENTS.md`: **8,686 characters**
- rough intuition: **~2,172 tokens**
- reduction versus old Custom Instructions alone: **24.7%**

The old real tandem also loaded repository instructions on top of the 11.5k global prompt, so comparisons against the old Custom Instructions alone remain conservative.

## Progressive context

- **12 task-triggered Skills**
- all Skill bodies together: **11,233 characters**, not intended to load together
- largest Skill: **2,012 characters** (`architecture-decision`)
- uninitialized canonical project default context: **825 characters** (~206 chars/4 rough tokens)

`LINEAGE.md`, tool adapters, contracts and eval files are on-demand/framework-maintenance evidence and are excluded from normal project warm-up.

## Quality evidence

- inherited Custom Instructions: **147 atomic rules / 22 static scenarios**;
- Progressive Framework Contract: **41 rules / 10 static scenarios**;
- anti-duplication gate across canonical instruction owners;
- branded registry: **7 preferred tools** with fallbacks and current-official-doc install policy;
- Codex Personal, Claude Personal, mixed-agent and Standalone layering covered by automated tests;
- source/install/adoption/update behavior covered by automated tests;
- Action-First Communication (minimum-sufficient output, explicit priority order) covered in both universal adapters and generated Standalone, with dedicated contract/scenario/test coverage.

Static checks prove workflow integrity, not empirical model-quality multiplication. Real-agent evaluation is optional and external to the normal Spec Kit workflow.
