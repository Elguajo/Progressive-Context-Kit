# Progressive Context Spec Kit — Getting Started

> **Human-only onboarding guide.** This file belongs to Framework Source and is deliberately excluded from the Project Runtime release.

## 1. Recommended path: download Project Runtime

For normal product work, do not clone/copy the entire Framework Source repository.

Download the latest release asset:

```text
Progressive-Context-Project-Runtime-v1.6.0.zip
```

from:

```text
https://github.com/Elguajo/Progressive-Context-Spec-Kit/releases/latest
```

Extract it into the directory that will become your project.

The initial framework surface should look like this:

```text
my-project/
├── .agents/
├── .claude/
├── .progressive/
├── AGENTS.md
└── CLAUDE.md
```

Everything Progressive-specific that does not need to be a native agent entrypoint lives under the hidden `.progressive/` directory.

## 2. No global setup is required for the default release

The main Project Runtime release uses the **Standalone profile**.

That means you do not need to install anything into:

```text
~/.claude/CLAUDE.md
~/.codex/AGENTS.md
```

before starting.

This is intentional: the primary download should work with the fewest setup steps and the least installation ambiguity.

## 3. Start Claude Code or Codex

Example with Claude Code:

```bash
cd /path/to/my-project
git init   # if needed
claude
```

Project-level Claude Skills stay in:

```text
.claude/skills/
```

Do not copy them to your user-level `~/.claude/skills/` directory as part of normal Project Runtime setup.

## 4. First prompt

For a new product:

```text
Use .progressive/prompts/START_NEW_PROJECT.md.

My idea:
<describe the problem, intended users, desired outcome, important constraints, and explicit non-goals>
```

Describe primarily **what** you want and the real constraints.

Do not preselect framework, database, hosting, state management, or directory structure unless they are genuine product/organizational requirements.

The workflow should determine appropriate scope, architecture, roadmap, implementation phases, and validation strategy.

## 5. What Progressive should maintain

```text
Idea
→ Project Brief
→ Architecture
→ Roadmap
→ Current Phase
→ Implementation
→ Validation
→ Completion Record / Handoff
→ Next Session
```

Runtime owners:

- `.progressive/project/PROJECT_BRIEF.md` — product truth;
- `.progressive/project/ARCHITECTURE.md` — current system truth;
- `.progressive/project/ROADMAP.md` — canonical phase order/status;
- `.progressive/phases/*` — execution and acceptance contracts;
- completed phase `Completion Record` — compact durable bridge;
- `.progressive/project/NEXT_SESSION.md` — overwriteable hot navigation;
- `.progressive/decisions/*` — consequential rationale when an ADR is justified.

You should not have to manually tell the agent which of these files to maintain during normal use.

## 6. Fresh-session continuity

After a meaningful session:

1. let the agent validate and hand off;
2. close the session completely;
3. start a fresh session in the same repository;
4. paste only the generated `NEXT SESSION PROMPT`;
5. do not manually re-explain the project unless something important was actually lost.

This is the practical continuity test Progressive is designed to pass.

## 7. What the agent should normally read

For normal product work, prefer the smallest sufficient context:

```text
repository behavior
+ Project Brief
+ Architecture
+ Roadmap
+ current Phase
+ immediate previous Completion Record when relevant
+ task-relevant code/tests
+ matching Skill/protocol
```

It should not recursively warm up from the entire `.progressive/` directory.

Human docs, migration evidence, framework tests, full completed phase bodies, and framework history are intentionally absent from the Runtime package.

## 8. Verify the Runtime

```bash
python3 .progressive/tools/audit.py --root .
python3 .progressive/tools/context_compile.py --root .
```

The Runtime audit checks project/runtime integrity only. Full behavior/framework contracts belong to Framework Source.

## 9. Personal deployment — optional advanced mode

Personal mode is still supported for users who deliberately want one user-global engineering layer shared across many repositories.

From a trusted Framework Source checkout:

Claude Code:

```text
global/CLAUDE.md → ~/.claude/CLAUDE.md
```

Codex:

```text
global/AGENTS.codex.md → ~/.codex/AGENTS.md
```

Then install:

```bash
python3 tools/init_project.py /path/to/project --profile personal --agent both --dry-run
python3 tools/init_project.py /path/to/project --profile personal --agent both
```

Do not stack the old long Custom Instructions prompt on top of Progressive Personal global instructions unless you intentionally want duplicated behavior.

## 10. Existing projects

Adoption remains a Framework Source operation because it needs reconciliation/update tooling rather than only the final Runtime payload:

```bash
python3 tools/init_project.py /path/to/existing-project --profile standalone --adopt-existing --dry-run
python3 tools/init_project.py /path/to/existing-project --profile standalone --adopt-existing
```

## 11. If you are developing Progressive itself

Clone the Framework Source repository instead of the Project Runtime release.

Framework Source intentionally contains visible development directories such as:

```text
global/
integrations/
profiles/
prompts/
templates/
tools/
docs/
```

Those files exist to develop and verify Progressive; they should not be copied wholesale into product repositories.

## 12. Main rule

Use Progressive as a workflow, not as another prompt collection you must manually manage.

The user mainly owns desired outcome and real decisions. The agent owns context routing, project state, implementation, validation, and continuity.
