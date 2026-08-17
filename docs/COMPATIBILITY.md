# Compatibility

## Codex Personal

Install `global/AGENTS.codex.md` as the user-level Codex guidance (`~/.codex/AGENTS.md` by default). Repository `AGENTS.md` uses `profiles/personal/AGENTS.md`; `.agents/skills/*` provides progressive Skills.

## Claude Code Personal

Install `global/CLAUDE.md` as `~/.claude/CLAUDE.md`. Repository `CLAUDE.md` imports `@AGENTS.md`; root `AGENTS.md` uses the same Personal repository router. `.claude/skills/*` mirrors Codex Skills. This avoids repeating universal behavior in project startup context.

## Standalone

When no compatible user-level global layer is available, install the Standalone profile. Root `AGENTS.md` becomes the generated universal + repository composition. `CLAUDE.md` still imports `@AGENTS.md`, so Claude receives the complete Standalone baseline without a separate home-level file.

## Mixed Codex + Claude

Install both user-level global files once, deploy one Personal repository router, and keep the shared `CLAUDE.md -> @AGENTS.md` adapter. Agent-specific Skills remain mirrored under `.agents/skills` and `.claude/skills`.

Other agents can consume root `AGENTS.md` and invoke files under `prompts/` manually when they support compatible repository instructions.
