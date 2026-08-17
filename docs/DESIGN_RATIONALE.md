# Design Rationale

Progressive Context optimizes **active context delivery**, not merely prompt length.

The design north star is:

> **Minimize active context, not available knowledge.**

The goal is not to make the framework smaller at any cost. The goal is to keep the full engineering knowledge and Spec-Driven structure available while loading only the subset needed for the current task.

The same progressive-disclosure principle applies on two axes:

1. **Project knowledge** — durable Project Brief / Architecture / Roadmap → current Phase → current task, with only a bounded immediate-previous `Completion Record` bridge. Completed phase bodies stay cold by default.
2. **Agent behavior** — universal high-frequency guarantees stay global; project routing stays repo-local; detailed conditional procedures stay Skills/protocols and load only when their triggers apply.

This preserves the useful behavior of a comprehensive Custom Instructions setup without forcing every engineering procedure into every request.

Additional design choices:

- Branded tools are preferred implementations behind stable capability names; fallbacks prevent brittleness.
- Tool availability is cached so agents do not repeatedly rediscover or re-request setup.
- Context compilation is deterministic and disposable; canonical docs remain truth.
- Existing repositories have a forensic adoption workflow instead of being forced through greenfield bootstrap.
- Inherited Custom Instructions behavior and new Progressive framework behavior are protected by separate contracts.
- LINEAGE exists for framework audits only and is explicitly excluded from normal context.
- Correctness, security, behavioral completeness, and evidence always outrank token savings.

The practical target is:

```text
Active Context =
Global Core
+ Repo Router
+ Current Project Slice
+ Current Task Skill/Protocol
+ Relevant Code
```

not:

```text
Huge Custom Instructions
+ Huge repository instructions
+ Entire project documentation
+ all completed phases
+ every procedure/integration
+ relevant code
```

## v1.6 — Runtime encapsulation

Real-project testing exposed a filesystem UX problem: although Progressive minimized active context, its old Starter copied the framework's development surface (`global/`, `integrations/`, `profiles/`, `prompts/`, `templates/`, `tools/`, and `docs/`) into every product repository.

v1.6 extends the same design principle to filesystem surface area:

> **Minimize active context and visible framework surface.**

Progressive now has one canonical Framework Source and one generated Project Runtime. The Runtime is not a second independently maintained kit; release tooling derives it from the same source files and rewrites source-layout paths into the hidden `.progressive/` runtime namespace.

The project-facing ownership model becomes:

```text
AGENTS.md / CLAUDE.md     agent entrypoints
.agents/ / .claude/      native task-triggered Skills
.progressive/project/     durable project truth
.progressive/phases/      execution contracts
.progressive/decisions/   consequential rationale
.progressive/system/      cold workflow protocols
.progressive/prompts/     entrypoint prompts
.progressive/templates/   creation templates
.progressive/tools/       runtime integrity/context helpers
```

Framework migration evidence, human onboarding, release tooling, source tests, profile generation, and framework contracts remain Framework Source concerns and are not shipped into normal product repositories.
