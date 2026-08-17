# Profiles

## Personal Codex — recommended

1. Put the exact contents of `global/AGENTS.codex.md` in Codex Custom Instructions.
2. Use root `AGENTS.md` with `profiles/personal/AGENTS.md` as its canonical framework prefix. Existing-project adoption may preserve project-specific instructions after the protected sentinel.
3. Let the router load detailed Skills/protocols only when their triggers apply.

v1.5 is **quality-first + tool-aware**: the global layer is intentionally close to 5,000 characters because
it owns high-frequency universal guarantees. The repository router remains project-specific.

## Standalone

Use `profiles/standalone/AGENTS.md` as root `AGENTS.md` when no compatible global layer
exists. It is generated from global + personal sources, so it is complete without creating a
second editable behavioral source.

## Claude Code

Personal Claude uses `global/CLAUDE.md` as `~/.claude/CLAUDE.md`. Project `CLAUDE.md` imports
the active root `@AGENTS.md`, so Claude receives the same repository router as Codex without
loading the Standalone profile on top of its user-global behavior.

Run `python3 tools/sync_profiles.py` to verify composition and active root mirror.

## Personal is agent-neutral at repository level

`profiles/personal/AGENTS.md` intentionally avoids vendor-specific universal behavior. Codex gets that layer from `global/AGENTS.codex.md`; Claude Code gets it from `global/CLAUDE.md`. Root `CLAUDE.md` imports the active root `AGENTS.md`, so the same repository profile works for either agent.
