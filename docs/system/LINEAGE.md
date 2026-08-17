# Lineage — Token-Efficient Spec Kit → Progressive Context Kit

**Framework-maintenance evidence only. Do not load this file during normal product work.**

This file records what was retained, redesigned, improved, or intentionally removed from `Elguajo/Token-Efficient-Spec-Kit` so future optimization does not accidentally erase useful behavior.

| Original mechanism | Progressive v1.7.x owner | Status | Rationale |
|---|---|---|---|
| Project Brief | `docs/project/PROJECT_BRIEF.md` | Retained | Canonical product truth |
| Architecture | `docs/project/ARCHITECTURE.md` | Retained | Canonical current system shape/boundaries |
| Roadmap | `docs/project/ROADMAP.md` | Retained | Canonical phase order/status pointer |
| Phase files | `docs/phases/*` | Retained | Execution/acceptance contracts |
| ADR | `docs/decisions/*` | Retained | Consequential decision rationale |
| NEXT_SESSION | `NEXT_SESSION.md` + `session-handoff` | Redesigned | Disposable navigation, not second spec |
| Decision Framework | `architecture-decision` Skill | Redesigned | Progressive A/B/C + stop/pivot semantics |
| Engineering Rules | Global contract + implementation/quality Skills | Redesigned | Single owners, less duplication |
| Creative Autonomy | Global contract + bootstrap/implementation | Retained/redistributed | Routine decisions remain autonomous |
| Project Doctor | `project-doctor` Skill | Redesigned | On-demand diagnosis |
| Session Handoff | `session-handoff` + `HANDOFF_PROTOCOL.md` | Redesigned | On-demand but mandatory for meaningful sessions |
| Workflow Self-Audit | `workflow-audit` + `tools/audit.py` | Improved | Machine-verifiable gates |
| Workflow Update Policy | `CHANGE_CONTROL.md` + installer | Improved | Project-owned state preservation |
| Token Efficiency | `CONTEXT_PROTOCOL.md` + budgets + compiler | Improved | Progressive routing + deterministic bundle |
| Tooling Profiles | Registry + `PROFILES.md` + tooling bootstrap | Restored/Improved | Branded preferred implementations retained |
| Semble | Tool registry/adapter | Retained | Preferred semantic discovery |
| Serena | Tool registry/adapter | Retained | Preferred symbol/refactor tooling |
| RTK | Tool registry/adapter | Retained | Preferred compact output |
| Superpowers | Tool registry/adapter | Retained | Preferred HOW discipline |
| gstack | Tool registry/adapter | Retained | Preferred challenge/QA/release layer |
| Context7 | Tool registry/adapter | Retained | Preferred fresh-doc provider |
| GitHub Spec Kit | Advanced Spec profile | Retained | Optional deep specification |
| `.specify/memory/constitution.md` governance | Global + Skills + protocols/contracts | Redesigned | Avoid duplicate always-loaded governance |
| Large monolithic operational prompts | Skills/protocols + short entry prompts | Redesigned | Progressive disclosure |
| Existing-project implicit handling | `ADOPT_EXISTING_PROJECT.md` + Skill | Improved | First-class forensic adoption workflow |
| Action-First Communication (Token v0.11) | `global/AGENTS.codex.md` + `global/CLAUDE.md` | Retained/Adapted | Minimum-sufficient user-facing output; no ADHD framing or separate always-on Skill |

## Non-regression rule

A framework change that removes an original capability must update this file with the reason **and** pass both inherited Behavior Contract and Framework Contract gates. Token reduction alone is not a sufficient reason to remove correctness, safety, project-state, handoff, or materially useful tooling behavior.
