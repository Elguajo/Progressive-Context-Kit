# Changelog

## 1.7.1 — 2026-08-18

- Added `docs/project/NEXT_SESSION.md` to the Default Read Set: it is now read on resume (both the preferred `tools/context_compile.py` path and the manual fallback in `AGENTS.md`), so hot next-action state actually reaches new sessions instead of being skipped.
- Changed the `NEXT SESSION PROMPT` block in `templates/NEXT_SESSION.template.md` to lead with the session's concrete `Next action` instead of pure boilerplate, so a pasted resume prompt carries distinguishing content (also improves auto-generated chat titles in client UIs that title from the first message).
- Compacted the `profiles/personal/AGENTS.md` / `AGENTS.md` context-routing line (dropped repeated `docs/project/` path prefixes) to stay within the unchanged 3,600-char hard budget; preserved the FW-036 Framework Contract anchor verbatim.
- No Behavior Contract or Framework Contract rules changed; all 80 unit tests, the framework/behavior contract audits, and the profile-mirror check pass unchanged.

## 1.7.0 — 2026-08-17

- Added **Action-First Communication** to both universal adapters (`global/AGENTS.codex.md`, `global/CLAUDE.md`): minimum-sufficient-information principle, explicit output priority (`Correctness > Safety > Task completeness > Actionability > Concision`), bounded numbered steps, tangent suppression, `location -> cause -> fix` error reporting, no speculative time estimates, and no manufactured next action after a complete request.
- Ported semantically from `Token-Efficient-Spec-Kit@v0.11.0`'s `## Action-first output` section, not copied mechanically: no ADHD framing, no new dependency, no separate always-on Skill — folded into the existing always-loaded universal contract.
- Standalone inherits the behavior through generated composition (`tools/sync_profiles.py`); the Personal repository router does not duplicate the universal block.
- Compacted existing wording in both global adapters to stay within the unchanged 5,000-char hard budgets and the 8,500/8,600-char combined Personal budgets, preserving every one of the 147 inherited Behavior Contract anchors and all 37 pre-existing Framework Contract rules.
- Added Framework Contract rules FW-038…FW-041 and a static `action-first-communication` scenario; recomputed `FRAMEWORK_IDS.sha256`.
- Extended `tools/tests/test_profiles.py` with Action-First regression coverage on both global adapters and on generated-vs-duplicated placement.
- Updated `docs/system/LINEAGE.md` and `docs/DESIGN_RATIONALE.md` to record the ported behavior.
- Confirmed the v1.4 Completion Record / Handoff Protocol and the v1.3 tooling-bootstrap model remain unchanged and were not re-derived from Token v0.10 (already superseded).

## 1.6.0 — 2026-08-17

- Split delivery into one canonical **Framework Source** repository and one generated **Project Runtime** release surface.
- Added hidden runtime encapsulation under `.progressive/`; product roots now expose only standard `AGENTS.md` / `CLAUDE.md` entrypoints plus hidden `.agents/`, `.claude/`, and `.progressive/`.
- Removed visible framework-development folders (`global/`, `integrations/`, `profiles/`, `prompts/`, `templates/`, `tools/`, `docs/`) from Project Runtime.
- Made the primary Project Runtime release zero-setup with the Standalone profile; Personal global adapters remain optional Framework Source deployment.
- Added `tools/build_runtime.py`, runtime path transformation, dedicated runtime audit, and dual-layout context/tooling helpers.
- Changed `init_project.py` to install/update the encapsulated Runtime layout while preserving project-owned `.progressive/project`, `.progressive/phases`, and `.progressive/decisions`.
- Kept `tools/build_starter.py` as a compatibility alias; the user-facing package is now named **Project Runtime**.
- Added release automation so version tags can build and publish the Runtime asset from Framework Source.
- Updated onboarding/README to make the Project Runtime release the primary download and Framework Source the development surface.

## 1.5.1 — 2026-08-17

- Added a dedicated human-only `docs/human/GETTING_STARTED.md` with explicit Personal/Standalone, Claude Code, Codex, new-project, fresh-session, and adoption instructions.
- Changed Starter packaging so `docs/human/` is excluded from project distributions: onboarding documentation remains available to the human but cannot become normal project context.
- Added regression coverage proving human-only docs are absent from both the built Starter and projects installed from it.
- Clarified that Claude project Skills remain inside `.claude/skills/`; Personal setup only installs `global/CLAUDE.md` to `~/.claude/CLAUDE.md`.
- Removed the leftover `prompts/BENCHMARK_CONTEXT.md` from the clean release and removed the older duplicate `docs/USAGE_GUIDE.md`.
- No inherited Behavior Contract rules, Framework Contract rules, normal context budgets, phase semantics, or runtime execution workflow were changed.

## 1.5.0 — 2026-08-17

- Clarified Progressive Context as a token-efficient Spec-Driven Development workflow rather than a prompt-minimization exercise.
- Added the design north star: **Minimize active context, not available knowledge.**
- Documented the two progressive-disclosure axes: project knowledge and agent behavior.
- Kept the v1.4 runtime architecture, 147 inherited behavior rules, 36 Progressive Framework Contract rules, phase Completion Records, context budgets, tooling model, installer, and validation behavior unchanged.
- Kept empirical model evaluation external/optional; no benchmark harness, benchmark suite, benchmark records, or benchmark-specific runtime tooling were added to the kit.

## 1.4.0 — 2026-08-17

- Added durable per-phase `Completion Record`s so completed work survives `NEXT_SESSION.md` overwrite without turning handoff files into history logs.
- Added a bounded phase-transition context bridge: `context_compile.py` carries only the immediate predecessor's Completion Record into the next active phase, never the full completed phase by default.
- Defined `NEXT_SESSION.md` as volatile hot context that is overwritten in place; durable outcomes/evidence/debt live with the completed phase, while version control remains the detailed technical history.
- Added completion-order guarantees: persist phase outcome first, then move Roadmap markers, then write the new hot handoff.
- Added audit warnings for legacy `[x]` phases that lack Completion Records, preserving upgrade compatibility instead of failing old projects.
- Expanded the Framework Contract from 30 to 36 rules with a dedicated phase-transition continuity scenario and compiler regression tests.
- Fixed stale Claude profile documentation that incorrectly said root `CLAUDE.md` imports the Standalone profile.

## 1.3.1 — 2026-08-16

- Fixed Claude Personal instruction duplication: project `CLAUDE.md` now imports active root `@AGENTS.md` instead of importing the Standalone profile directly.
- Added canonical `global/CLAUDE.md` for `~/.claude/CLAUDE.md`, semantically aligned with the universal Codex engineering contract while respecting Claude-specific instruction loading.
- Made the Personal repository router vendor-neutral so one repository profile can serve Codex, Claude Code, or both.
- Added installer `--agent codex|claude|both` deployment metadata/guidance without automatically modifying home-level agent configuration.
- Added static contract/test coverage for Codex Personal, Claude Personal, mixed-agent, and Standalone layering.
- Updated compatibility, usage, ownership, and Starter deployment documentation.

## 1.3.0 — 2026-08-16

- Restored Semble, Serena, RTK, Superpowers, gstack, Context7, and conditional GitHub Spec Kit as explicit preferred implementations behind stable capabilities.
- Added `TOOL_REGISTRY.json`, per-tool adapters, `tooling-bootstrap`, and persisted `TOOLING_STATUS.json`; missing materially useful tools are offered for current-official-doc installation instead of silently forgotten.
- Added first-class `ADOPT_EXISTING_PROJECT.md` / `existing-project-adoption` with safe instruction preservation and installer `--adopt-existing` / `--finalize-adoption`.
- Added deterministic `context_compile.py` and optional `CONTEXT_MANIFEST.json` for compact context assembly.
- Added framework-maintenance-only `LINEAGE.md` mapping Token-Efficient Spec Kit mechanisms to Progressive owners.
- Added a separate 26-rule Progressive Framework Contract with 6 static scenarios while retaining the inherited 147-rule / 22-scenario Behavior Contract.
- Split static contract scenarios from controlled real-agent eval documentation.
- Added canonical exact/near-duplication audit.
- Expanded automated tests for tooling, adoption, compiler, framework contract, and duplication regression.

## 1.2.0 — 2026-08-16

- Switched optimization objective from minimum context to quality-first bounded context.
- Expanded the global Codex contract for quality while keeping a safety margin below the 5,000-character target (4,836 characters).
- Added `implementation-execution` Skill; total progressive Skills: 10.
- Restored detailed A/B/C decision format, exact stop/pivot behavior, review tradeoff format, implementation completeness, validation failure classification, security refusal patterns, durable-document approval semantics, and completion-report behavior.
- Replaced section-only migration confidence with `BEHAVIOR_CONTRACT.json`: 147 atomic rules with active owners and semantic anchors.
- Added 22 behavior scenarios covering every atomic rule plus `tools/behavior_contract.py`.
- Added controlled model-evaluation protocol and explicit prohibition on unmeasured “N× quality” claims.
- Raised context budgets deliberately to preserve high-frequency engineering guarantees.
- Extended Starter/installer/audit/test tooling to carry and verify behavior evidence.

## 1.1.1 — 2026-08-16

- Synced `global/AGENTS.codex.md` to the final recommended Codex Custom Instructions.
- Added explicit `profiles/personal/AGENTS.md`; root `AGENTS.md` is now a verified mirror.
- Added generated Standalone composition and profile drift checks.
- Changed Claude adapter to import the complete Standalone profile so Claude does not depend on Codex Personalization.
- Added `documentation-governance` Skill to preserve durable-document approval behavior without global prompt bloat.
- Added pinned SHA-256 migration evidence for the original 12-section Custom Instructions.
- Tightened Personal context budgets and expanded audit/test coverage.
- Updated starter/install tooling for both profiles.

## 1.1.0 — 2026-08-15

- Added Personal Codex global layer plus slim repository router.
- Added migration coverage from the previous 12-section Custom Instructions.
- Added Personal and Standalone context reporting and safe project initialization.
