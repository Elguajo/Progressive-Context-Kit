# User-level global instructions

This directory contains the recommended universal engineering layer for each supported agent.

- `AGENTS.codex.md` → install/review as `~/.codex/AGENTS.md` for Codex Personal deployment.
- `CLAUDE.md` → install/review as `~/.claude/CLAUDE.md` for Claude Code Personal deployment.

These files own universal engineering behavior. The repository `AGENTS.md` owns project/context/workflow routing. Do not copy either global file into repository `AGENTS.md` in Personal mode.

The installer never modifies home-level agent configuration automatically. Install the matching user-level instruction file deliberately, then use `tools/init_project.py` for repository deployment.

For Claude Code, project Skills stay under the project's `.claude/skills/`; they are not part of the one-time `~/.claude/CLAUDE.md` installation.

For mixed Codex + Claude Personal deployment, install both user-level files once and keep one shared repository `AGENTS.md`; the project `CLAUDE.md` imports that active repository profile.

For first-time setup see `docs/human/GETTING_STARTED.md` in the full source distribution.
