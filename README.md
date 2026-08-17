# Progressive Context Spec Kit v1.6.0

> 🇷🇺 Русская версия: [`README_RU.md`](README_RU.md) · подробный гайд: [`docs/human/GETTING_STARTED.ru.md`](docs/human/GETTING_STARTED.ru.md)

A **quality-first, token-efficient Spec-Driven Development workflow** for AI coding agents.

> **Minimize active context, not available knowledge.**

## Start here — most users

Do **not** copy this whole repository into your product.

This repository is the **Framework Source** used to develop, test, and release Progressive Context itself.

For a new project, download the latest release asset:

**`Progressive-Context-Project-Runtime-v1.6.0.zip`**

from **GitHub Releases**: https://github.com/Elguajo/Progressive-Context-Spec-Kit/releases/latest

The Project Runtime is intentionally small and self-contained. After extraction, Progressive occupies only standard agent entrypoints plus hidden framework directories:

```text
my-project/
├── .agents/                  # agent Skills
├── .claude/                  # Claude Code Skills
├── .progressive/             # Progressive project memory + runtime
├── AGENTS.md                 # repository router
├── CLAUDE.md                 # Claude adapter
└── <your application files>
```

You will **not** get visible framework folders such as `global/`, `integrations/`, `profiles/`, `prompts/`, `templates/`, `tools/`, or `docs/` in the product root.

The default Project Runtime uses the **Standalone profile**, so a new user can extract it and start Claude Code or Codex without first configuring home-level global instructions.

Start a new project with:

```text
Use .progressive/prompts/START_NEW_PROJECT.md.

My idea:
<describe the desired product, users, real constraints, and explicit non-goals>
```

## One framework, two surfaces

```text
Progressive Context — canonical Framework Source
                    │
                    ├── Framework Source
                    │   GitHub repository
                    │   development / tests / migration / release tooling
                    │
                    └── Project Runtime
                        GitHub Release asset
                        minimal hidden runtime placed in real projects
```

The Runtime is **generated from this repository**. It is not maintained as a second independent Spec Kit, so the two surfaces cannot intentionally drift.

## Framework Source

Use this repository when you want to:

- develop Progressive Context itself;
- change behavior contracts, Skills, protocols, or installers;
- maintain Codex / Claude adapters;
- run migration and framework regression tests;
- build the Project Runtime release.

Human onboarding lives at `docs/human/GETTING_STARTED.md` (Russian: `docs/human/GETTING_STARTED.ru.md`) and stays source-only.

## Build the Project Runtime

```bash
python3 tools/build_release.py
```

Output:

```text
dist/Progressive-Context-Project-Runtime-v1.6.0.zip
dist/Progressive-Context-Project-Runtime-v1.6.0.manifest.json
dist/SHA256SUMS.txt
```

`tools/build_release.py` is the canonical release entrypoint: it validates Framework Source, builds Runtime, audits the extracted Runtime, and writes release metadata. `tools/build_runtime.py` is the lower-level packaging step.

`tools/build_starter.py` remains as a compatibility alias, but **Project Runtime** is the user-facing name from v1.6 onward.

## Personal profile — optional advanced setup

The release Runtime defaults to zero-setup Standalone behavior.

If you deliberately want Personal deployment across many repositories, Framework Source still provides:

- `global/AGENTS.codex.md` → `~/.codex/AGENTS.md`
- `global/CLAUDE.md` → `~/.claude/CLAUDE.md`

Then install with the Personal profile from a trusted Framework Source checkout:

```bash
python3 tools/init_project.py /path/to/project --profile personal --agent both --dry-run
python3 tools/init_project.py /path/to/project --profile personal --agent both
```

The installer never modifies home-level agent configuration automatically.

## Runtime context model

Normal product work progressively routes:

```text
repository behavior
        ↓
.progressive/project/PROJECT_BRIEF.md
        ↓
.progressive/project/ARCHITECTURE.md
        ↓
.progressive/project/ROADMAP.md
        ↓
current .progressive/phases/*
        ↓
bounded prior Completion Record
        ↓
matching Skill + protocol + relevant code/tests
```

Completed phases, framework history, human docs, migration evidence, and framework-development tests remain out of normal warm-up.

## Preferred tooling

The Framework Source retains **Semble, Serena, RTK, Superpowers, gstack, Context7**, with **GitHub Spec Kit** as conditional Advanced Spec Mode. Tool selection remains task-routed; installed does not mean loaded or invoked.

## Verify Framework Source

```bash
python3 tools/behavior_contract.py
python3 tools/framework_contract.py
python3 tools/duplication_audit.py
python3 tools/audit.py
python3 tools/build_runtime.py
python3 -m unittest discover -s tools/tests -v
```

## Verify a Project Runtime

From an extracted project:

```bash
python3 .progressive/tools/audit.py --root .
python3 .progressive/tools/context_compile.py --root .
```

Static framework gates remain in Framework Source; the Project Runtime carries only runtime integrity and project execution machinery.
