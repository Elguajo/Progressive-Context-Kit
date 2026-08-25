<div align="center">

# Progressive Context Kit

**Token-Efficient · Quality-First · Spec-Driven**

[![Release](https://img.shields.io/github/v/release/Elguajo/Progressive-Context-Kit?label=release)](https://github.com/Elguajo/Progressive-Context-Kit/releases/latest)
[![CI](https://github.com/Elguajo/Progressive-Context-Kit/actions/workflows/audit.yml/badge.svg)](https://github.com/Elguajo/Progressive-Context-Kit/actions/workflows/audit.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Contributing](https://img.shields.io/badge/contributions-guide-informational.svg)](CONTRIBUTING.md)

🇷🇺 Русская версия: [`README_RU.md`](README_RU.md) · detailed guide: [`docs/human/GETTING_STARTED.md`](docs/human/GETTING_STARTED.md)
</div>

Progressive Context Kit is a quality-first development framework for AI coding agents. It gives Codex and Claude Code durable project memory, task-routed guidance, and a verifiable workflow without turning every session into a full repository briefing.

> **Minimize active context, not available knowledge.**

## What you get

- a compact starting point for AI-assisted product work;
- durable project state that survives individual chat sessions;
- planning and validation that scale with the task's risk and uncertainty;
- a self-contained Runtime for projects, plus a separately maintained Framework Source.

## Start in 2 minutes

For a new product:

1. [Download the latest Project Runtime](https://github.com/Elguajo/Progressive-Context-Kit/releases/latest) and extract it into the directory that will contain your project.
2. Open that directory in Codex or Claude Code. The default Runtime is self-contained: no global setup is required.
3. Send this first prompt:

   ```text
   Use .progressive/prompts/START_NEW_PROJECT.md.

   My idea:
   <describe the desired product, users, real constraints, and explicit non-goals>
   ```

Current stable asset: `Progressive-Context-Project-Runtime-v2.0.0.zip`.

For an existing product repository, do not extract a Runtime ZIP over project-owned files. Use the [adoption path](docs/human/GETTING_STARTED.md#10-existing-projects) from a trusted Framework Source checkout instead.

## Who it is for

Use Progressive Context when AI coding agents help build or maintain a real software project and you want its decisions, progress, and validation evidence to survive beyond one chat session. It is designed for projects that benefit from explicit scope, task-routed instructions, and compact durable project memory.

It is not a replacement for CI/CD, an issue tracker, source control, security review, or team documentation. It adds an agent-facing execution and continuity layer alongside those systems.

## Compared with a single `AGENTS.md`

A single `AGENTS.md` can be enough for a small, stable repository. Progressive Context keeps that familiar entrypoint while making larger or longer-running work easier to resume and verify.

| Concern | Single long `AGENTS.md` | Progressive Context |
| --- | --- | --- |
| Active instructions | One document carries universal and conditional guidance. | The router stays small; task-specific Skills and protocols load only when needed. |
| Project continuity | Relies mainly on the current chat and repository history. | Durable project state makes the next task or session explicit. |
| Change planning | Usually decided in the prompt each time. | Planning depth follows risk, uncertainty, and scope. |
| Verification | Expectations live in prose. | Task-relevant validation provides checkable evidence. |

## FAQ

**Do I need Git?** No. You can extract the Runtime and begin without it. Git remains strongly recommended for a real product because it preserves change history and supports collaboration.

**Do I need global setup?** No. The default Standalone Runtime includes the repository-level instructions and Skills it needs. Personal deployment is optional for users who intentionally share one global engineering layer across repositories.

**Can I add it to an existing project?** Yes, using `tools/init_project.py --adopt-existing` from a trusted Framework Source checkout. Run it with `--dry-run` first; do not extract the Runtime archive over an existing project.

**What is stored in `.progressive/`?** Runtime tools and prompts plus project memory, phases, completion history, and consequential decisions. Project-owned state is preserved during framework updates.

## Learn more

- [`Getting started`](docs/human/GETTING_STARTED.md) — installation, adoption, and first-session guidance.
- [`Technical reference`](docs/human/TECHNICAL_REFERENCE.md) — Runtime architecture, project state, profiles, validation, and Framework Source maintenance.
- [`How Progressive Context works`](docs/human/HOW_PROGRESSIVE_CONTEXT_WORKS.md) and the [`Project memory model`](docs/human/PROJECT_MEMORY_MODEL.md).
- [`Glossary`](docs/human/GLOSSARY.md) and [`updating Runtime safely`](docs/human/UPDATING_RUNTIME.md).

## Contributing

Use this repository to develop Progressive Context Kit itself. See [`CONTRIBUTING.md`](CONTRIBUTING.md) for the canonical verification path and contribution rules.

## Security

See [`SECURITY.md`](SECURITY.md) for the project's security policy.

## License

Released under the [MIT License](LICENSE).
