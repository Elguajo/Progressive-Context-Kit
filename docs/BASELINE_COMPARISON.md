# Baseline Comparison — v1.6.0 Deployment + Tooling

Counts use deterministic Unicode characters. `chars / 4` is rough intuition only, not exact tokenizer/billing output.

## Archived old Custom Instructions

- **11,540 characters**
- rough intuition: **~2,885 tokens**
- hash-pinned under `docs/migration/`

## Codex Personal always-loaded layers

- `global/AGENTS.codex.md`: **4,836 characters**
- `profiles/personal/AGENTS.md`: **3,581 characters**
- combined: **8,417 characters**
- rough intuition: **~2,104 tokens**
- reduction versus the old Custom Instructions **alone**: **27.1%**

## Claude Personal always-loaded layers

- `global/CLAUDE.md`: **4,950 characters**
- shared `profiles/personal/AGENTS.md`: **3,581 characters**
- combined: **8,531 characters**
- rough intuition: **~2,133 tokens**
- reduction versus the old Custom Instructions **alone**: **26.1%**

Project `CLAUDE.md` imports only the active root `@AGENTS.md`; it does not import Standalone directly in Personal mode. This prevents a second copy of universal behavior from entering Claude startup context.

## Standalone

- composed root `AGENTS.md`: **8,603 characters**
- rough intuition: **~2,151 tokens**
- reduction versus old Custom Instructions alone: **25.5%**

The old real tandem also loaded repository instructions on top of the 11.5k global prompt, so comparisons against the old Custom Instructions alone remain conservative.

## Progressive context

- **12 task-triggered Skills**
- all Skill bodies together: **11,233 characters**, not intended to load together
- largest Skill: **2,012 characters** (`architecture-decision`)
- uninitialized canonical project default context: **825 characters** (~206 chars/4 rough tokens)

`LINEAGE.md`, tool adapters, contracts and eval files are on-demand/framework-maintenance evidence and are excluded from normal project warm-up.

## Quality evidence

- inherited Custom Instructions: **147 atomic rules / 22 static scenarios**;
- Progressive Framework Contract: **36 rules / 8 static scenarios**;
- anti-duplication gate across canonical instruction owners;
- branded registry: **7 preferred tools** with fallbacks and current-official-doc install policy;
- Codex Personal, Claude Personal, mixed-agent and Standalone layering covered by automated tests;
- source/install/adoption/update behavior covered by automated tests.

Static checks prove workflow integrity, not empirical model-quality multiplication. Real-agent evaluation is optional and external to the normal Spec Kit workflow.
