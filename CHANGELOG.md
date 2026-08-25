# Changelog

## 2.0.0 — 2026-08-25

- Added **machine-readable Skill activation semantics** (`automatic`, `explicit`, `both`) across all canonical Skills, with source/runtime validation and mirror-safe regression coverage. Existing routing behavior remains unchanged; metadata now makes activation intent inspectable without adding always-loaded context.
- Added a first-class **Routing Integrity** contract and validator. Automatic Skills must be reachable from the repository router, explicit-only Skills remain intentional exceptions, required protocol/prompt paths must exist, and delegation edges must resolve to valid auto-capable Skills. The same contract validates Framework Source and generated Project Runtime.
- Added the **Cold-Start Runtime Transfer Eval**: eight fresh-session scenarios covering DIRECT/FOCUSED greenfield work, existing-project adoption, unclear bugs, architecture forks, session continuation, post-completion change requests, and high-risk FULL planning. The harness separates empirical transfer evidence from static contract evidence and refuses to call partial/rescued runs a transfer pass.
- Added the **Unified Progressive Gate** (`python3 tools/gate.py`) as the single Framework Source verification entrypoint. CI, release preparation, and workflow-audit now delegate to the same ordered source-level checks instead of maintaining parallel verification lists. A Gate PASS remains explicitly scoped to static/integrity evidence, not model-quality proof.
- Added the **Tool Adapter Protocol** around the existing `TOOL_REGISTRY.json`: stable capabilities are separated from replaceable branded implementations, with explicit preferred/avoid conditions, safe fallbacks, approval boundaries, current-official-source requirements, and on-demand loading. The adapter contract is validated both before release and inside Project Runtime.
- Added compact **Ubiquitous Language** support owned by `PROJECT_BRIEF.md`, not by a new glossary layer. Domain terms are optional, bounded (prefer 0–12), evidence-grounded during adoption, updated only when semantics materially change, and protected by Runtime Audit warnings against duplicate or oversized vocabulary.
- Strengthened Progressive architectural guarantees without expanding the always-loaded kernel: the release keeps **9,036 always-loaded characters** in the Personal Codex profile while protecting 147 inherited Behavior Contract rules, 68 Framework Contract rules, 13 Progressive Context invariants, Routing Integrity, and Tool Adapter integrity.
- Added deterministic **release preparation** for `release/vX.Y.Z`: one versioned notes file drives `VERSION`, stable Runtime asset references, and `CHANGELOG.md`; the full Progressive Gate runs before an immutable tag is created, and GitHub Release assets are published only when the tag points to the exact verified commit.
- Validation snapshot before cutting the release: **Progressive Gate 11/11** and **177/177 unit/regression tests passing** on `main`.

## 1.9.0 — 2026-08-20

- Added **Execution Efficiency** guarantees to the universal contract and `implementation-execution`/`systematic-debugging` Skills: batched independent reconnaissance, bounded-inspection grounding, single-pass environment-prerequisite probing, convergent validation, a repeated-failure pivot rule, and bounded/coarse polling discipline instead of short-interval spin-checks. Covered by new Framework Contract rules, static scenarios, and regression tests (`tools/tests/test_execution_efficiency.py`).
- Added the **real-agent evaluation and Autoresearch loop**: a standardized paired-run eval schema, an analyzer that gates efficiency candidates behind a quality pass/fail, and an Autoresearch experiment lifecycle (registry, evidence-backed experiment records, CLI, release-time validation via `tools/autoresearch.py validate`) so efficiency changes to the framework must be measured, not just asserted (`docs/evals/agent/`, `tools/autoresearch.py`, `tools/analyze_agent_eval.py`, `tools/prepare_agent_benchmark.py`).
- Adopted the **Progressive-aware v2.5** architecture (`docs/migration/CODEX_CUSTOM_INSTRUCTIONS_V2_5.md`): the always-loaded global adapters (`global/AGENTS.codex.md`, `global/CLAUDE.md`) now delegate detailed testing policy, variable-option architecture decisions, and implementation-coupled documentation-governance procedures to their owning Skills, keeping only universal role/classification/grounding/safety/completion behavior always loaded. Adopted the underlying policy improvements: architecture decisions present all-and-only materially different options instead of a fixed A/B/C menu; substantial testable work may add a lightweight dev-only test framework autonomously within bounded scope; implementation-coupled docs (README usage, API examples, comments/docstrings) update automatically while durable governance stays approval-gated; completion reports are result-first.
- Raised the always-loaded hard character budgets to match the v2.5 target that shipped in the migration doc but had not yet been wired into enforcement: global adapters 5,000 → **5,500** chars each, Personal combined (global + repo router) 8,500/8,600 → **9,100** chars, Standalone composition 9,000 → **9,300** chars (`tools/audit.py`, `tools/tests/test_context.py`, `tools/tests/test_progressive_context_invariants.py`). The reduction-vs-archived-custom-instructions regression floor was recalibrated from >25% to >20% to match the real, larger v2.5 footprint.
- Fixed the v2.5 merge itself, which had left `main`'s `audit` CI failing since the first Progressive-aware v2.5 commit: reconciled 72 stale Behavior Contract anchors in `docs/migration/BEHAVIOR_CONTRACT.json` against the reworded/relocated kernel and Skill text (updating anchors for pure rewording, relocating the test-framework-approval rule to `implementation-execution/SKILL.md` where the policy now actually lives), restored several safety/quality clauses that were dropped rather than relocated during the kernel rewrite (lockfile/vendored-file caution, overlapping-edit integration, explicit fact/inference/assumption distinction, the trivial-only-after-high-risk and no-fake-options guardrails, "evidence rather than generic doctrine"), and regenerated the `.claude/skills` mirrors (`tools/sync_skills.py --apply`) and `profiles/standalone/AGENTS.md` (`tools/sync_profiles.py --apply`), which had drifted from their `.agents/skills` canonical sources.
- Synced `README_RU.md` with the current Progressive Context architecture and clarified evidence-driven-evolution positioning.
- Added **adaptive planning depth**: `project-bootstrap` and change requests now route through DIRECT / FOCUSED / FULL specification depth instead of one fixed procedure, protected by new Framework Contract rules and static evaluation coverage (`docs/system/PLANNING_DEPTH.md`, `prompts/START_NEW_PROJECT.md`, `prompts/CHANGE_REQUEST.md`).
- Tightened `architecture-decision` option formatting: each option now renders as a single bolded-label bullet with flowing prose and inline code spans for technical identifiers, instead of a per-attribute sub-bullet breakdown.
- Fixed post-release documentation drift: `README.md`/`README_RU.md`/`docs/human/GETTING_STARTED(.ru).md` still pointed at the `v1.8.0` runtime zip, and `docs/TOKEN_BUDGETS.md` still documented the pre-v1.9.0 5,000/8,500/8,600/9,000 char limits instead of the 5,500/9,100/9,300 limits `tools/audit.py` actually enforces. `tools/audit.py` now checks both against their canonical source (`VERSION`, the hard-budget constants) so they can't drift silently again.
- Fixed a Behavior Contract anchor regression introduced by the option-formatting change above: `DEC-03`/`DEC-04`/`DEC-05` anchored the literal string `"maintenance impact, and when appropriate"` in `architecture-decision/SKILL.md`, which the reformatted text no longer contained; updated the anchors to the new wording.

## 1.8.0 — 2026-08-18

- Added durable **phase completion reports**: an additive completion-report layer on top of phase execution, preserving v1.7.2 compatibility, cold-context behavior, project-owned history, and hard token-budget invariants (`templates/PHASE_COMPLETION.template.md`, `templates/PHASE.template.md`, `tools/runtime_layout.py`).
- Added a formal **Progressive Context Invariants** contract (`docs/contracts/PROGRESSIVE_CONTEXT_INVARIANTS.json` + pinned `PROGRESSIVE_CONTEXT_INVARIANT_IDS.sha256`) and wired it into `tools/framework_contract.py` / `tools/init_project.py`, with dedicated regression coverage (`tools/tests/test_progressive_context_invariants.py`, `tools/tests/test_completion_reports.py`).
- Expanded `docs/system/HANDOFF_PROTOCOL.md` and `session-handoff/SKILL.md` (canonical `.agents/skills`, mirrored `.claude/skills`) to **enforce single-focus `NEXT_SESSION.md` continuation** — resume state must carry one concrete next action, not a list — and updated `templates/NEXT_SESSION.template.md` to match.
- Fixed `tools/build_runtime.py` so empty runtime state directories (`.progressive/completions/`, `.progressive/decisions/`, `.progressive/phases/`) survive packaging into the release ZIP instead of being silently dropped.
- Added a full set of **human-only visual explanations** (`docs/human/VISUAL_EXPLANATIONS.md` plus diagrams under `docs/visuals/`: Progressive Context overview, phase-completion lifecycle, source→runtime release, layer ownership, framework update safety, project memory model, session context flow, tool routing, user onboarding) and companion human guides (`docs/human/HOW_PROGRESSIVE_CONTEXT_WORKS.md`, `PROJECT_MEMORY_MODEL.md`, `UPDATING_RUNTIME.md`, each with a Russian translation), linked from `README.md` / `README_RU.md`. These are guarded as source-only and asserted (by test) to never enter the Runtime ZIP, so the always-loaded agent context is unchanged.
- Refreshed `docs/human/GETTING_STARTED.md` / `.ru.md` onboarding for v1.8.0 and the new modular human docs.
- No inherited Behavior Contract or previously-pinned Framework Contract rule changed; the new Progressive Context Invariants are additive and covered by their own regression tests.

## 1.7.2 — 2026-08-18

- Broadened the `session-handoff` router trigger (`profiles/personal/AGENTS.md` / generated `AGENTS.md` / `profiles/standalone/AGENTS.md`) from "meaningful implementation/review session ending" to also fire on "session ending or user-only decision/blocker", so an agent pausing mid-phase for user confirmation is routed to handoff instead of silently ending the turn.
- Added an explicit invariant to `session-handoff/SKILL.md` (`.agents/skills` canonical, mirrored to `.claude/skills`): never end a turn with only "waiting for confirmation/next action is X" — persist state and supply the ready-to-copy continuation prompt before yielding to the user.
- Updated `docs/BASELINE_COMPARISON.md` always-loaded character counts to the current measured values; all combined budgets remain within their unchanged hard limits (Codex 8,491/8,500, Claude 8,547/8,600, Standalone 8,672/9,000, personal router 3,552/3,600).
- No Behavior Contract or Framework Contract rules changed; audits, duplication check, and profile/skill-mirror checks pass unchanged (147/22 behavior, 41/10 framework).

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
